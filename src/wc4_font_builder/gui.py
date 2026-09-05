from __future__ import annotations

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .builder import BuildRequest, execute
from .scanner import TextScanError
from .subset import AnalysisReport, BuildReport, FontBuildError


def _summary(report: AnalysisReport | BuildReport) -> str:
    lines = [
        f"扫描文件：{report.scannedFileCount}",
        f"实际文本字符种类：{report.uniqueTextCodepoints}",
        f"动态/可选字符种类：{report.optionalTextCodepoints}",
        f"源字体 glyph：{report.sourceGlyphs}",
    ]
    if isinstance(report, BuildReport):
        lines.extend([
            f"输出 glyph：{report.outputGlyphs}",
            f"源字体大小：{report.sourceBytes:,} 字节",
            f"输出字体大小：{report.outputBytes:,} 字节",
            f"体积缩减：{report.reductionPercent:.3f}%",
            f"关键 metrics 保持：{'是' if report.metricsPreserved else '否'}",
        ])
    else:
        lines.extend([
            f"源字体大小：{report.sourceBytes:,} 字节",
            f"请求字符：{report.requestedCodepoints}",
            f"源字体可覆盖：{report.sourceSupportedRequestedCodepoints}",
        ])
    lines.extend([
        f"必需字符缺失：{len(report.missingRequired)}",
        f"动态/可选字符缺失：{len(report.missingOptionalText)}",
        f"安全字符缺失：{len(report.missingSafe)}",
    ])
    if report.missingRequired:
        preview = "、".join(item["codepoint"] for item in report.missingRequired[:16])
        lines.append(f"缺失必需字符示例：{preview}")
    return "\n".join(lines)


class FontBuilderApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=14)
        self.master = master
        self.text_inputs: list[Path] = []
        self.extra_character_files: list[Path] = []
        self.font_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.report_var = tk.StringVar()
        self.profile_var = tk.StringVar(value="wc4")
        self.safe_set_var = tk.StringVar(value="自动")
        self.retain_gids_var = tk.BooleanVar(value=False)
        self.allow_missing_var = tk.BooleanVar(value=False)
        self.extra_chars_var = tk.StringVar()
        self.status_var = tk.StringVar(value="就绪")
        self._results: queue.Queue[tuple[str, object]] = queue.Queue()
        self._build_ui()

    def _build_ui(self) -> None:
        self.master.title("WC4 Font Builder v1")
        self.master.minsize(760, 650)
        self.pack(fill="both", expand=True)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(9, weight=1)

        ttk.Label(self, text="源字体").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.font_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(self, text="选择字体", command=self._pick_font).grid(row=0, column=2)

        ttk.Label(self, text="扫描模式").grid(row=1, column=0, sticky="w", pady=4)
        profile_frame = ttk.Frame(self)
        profile_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8)
        ttk.Combobox(profile_frame, textvariable=self.profile_var, values=("wc4", "generic"), state="readonly", width=14).pack(side="left")
        ttk.Label(profile_frame, text="wc4 = 只读取 stringtable 的实际显示文本（推荐）").pack(side="left", padx=12)

        ttk.Label(self, text="文本输入").grid(row=2, column=0, sticky="nw", pady=4)
        input_frame = ttk.Frame(self)
        input_frame.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=8)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        self.input_list = tk.Listbox(input_frame, height=7, selectmode=tk.EXTENDED)
        self.input_list.grid(row=0, column=0, rowspan=4, sticky="nsew")
        input_scroll = ttk.Scrollbar(input_frame, orient="vertical", command=self.input_list.yview)
        input_scroll.grid(row=0, column=1, rowspan=4, sticky="ns")
        self.input_list.configure(yscrollcommand=input_scroll.set)
        ttk.Button(input_frame, text="添加文件", command=self._add_text_files).grid(row=0, column=2, padx=8, sticky="ew")
        ttk.Button(input_frame, text="添加目录", command=self._add_text_dir).grid(row=1, column=2, padx=8, sticky="ew")
        ttk.Button(input_frame, text="移除选中", command=self._remove_selected).grid(row=2, column=2, padx=8, sticky="ew")
        ttk.Button(input_frame, text="清空", command=self._clear_inputs).grid(row=3, column=2, padx=8, sticky="ew")

        ttk.Label(self, text="输出字体").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.output_var).grid(row=4, column=1, sticky="ew", padx=8)
        ttk.Button(self, text="选择输出", command=self._pick_output).grid(row=4, column=2)

        ttk.Label(self, text="JSON 报告").grid(row=5, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.report_var).grid(row=5, column=1, sticky="ew", padx=8)
        ttk.Button(self, text="选择报告", command=self._pick_report).grid(row=5, column=2)

        ttk.Label(self, text="额外字符").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.extra_chars_var).grid(row=6, column=1, sticky="ew", padx=8)
        ttk.Button(self, text="额外字符文件", command=self._add_extra_file).grid(row=6, column=2)

        options = ttk.Frame(self)
        options.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(8, 4))
        ttk.Label(options, text="安全字符集").pack(side="left")
        ttk.Combobox(options, textvariable=self.safe_set_var, values=("自动", "none", "minimal", "wc4"), state="readonly", width=10).pack(side="left", padx=(6, 18))
        ttk.Checkbutton(options, text="保留 GID 空洞（实验）", variable=self.retain_gids_var).pack(side="left", padx=6)
        ttk.Checkbutton(options, text="允许必需字符缺失（不推荐）", variable=self.allow_missing_var).pack(side="left", padx=6)

        actions = ttk.Frame(self)
        actions.grid(row=8, column=0, columnspan=3, sticky="ew", pady=8)
        self.analyze_button = ttk.Button(actions, text="只分析覆盖", command=lambda: self._start(True))
        self.analyze_button.pack(side="left")
        self.build_button = ttk.Button(actions, text="生成精简字体", command=lambda: self._start(False))
        self.build_button.pack(side="left", padx=8)
        ttk.Label(actions, textvariable=self.status_var).pack(side="right")

        self.log = tk.Text(self, height=13, wrap="word", state="disabled")
        self.log.grid(row=9, column=0, columnspan=3, sticky="nsew")
        log_scroll = ttk.Scrollbar(self, orient="vertical", command=self.log.yview)
        log_scroll.grid(row=9, column=3, sticky="ns")
        self.log.configure(yscrollcommand=log_scroll.set)

    def _pick_font(self) -> None:
        selected = filedialog.askopenfilename(title="选择完整源字体", filetypes=(("OpenType 字体", "*.otf *.ttf"), ("所有文件", "*.*")))
        if selected:
            self.font_var.set(selected)
            if not self.output_var.get():
                source = Path(selected)
                self.output_var.set(str(source.with_name(source.stem + "_subset" + source.suffix)))
            if not self.report_var.get():
                self.report_var.set(str(Path(self.output_var.get()).with_suffix(".report.json")))

    def _pick_output(self) -> None:
        selected = filedialog.asksaveasfilename(title="保存精简字体", defaultextension=".otf", filetypes=(("OpenType 字体", "*.otf"), ("TrueType 字体", "*.ttf"), ("所有文件", "*.*")))
        if selected:
            self.output_var.set(selected)
            if not self.report_var.get():
                self.report_var.set(str(Path(selected).with_suffix(".report.json")))

    def _pick_report(self) -> None:
        selected = filedialog.asksaveasfilename(title="保存 JSON 报告", defaultextension=".json", filetypes=(("JSON", "*.json"), ("所有文件", "*.*")))
        if selected:
            self.report_var.set(selected)

    def _add_text_files(self) -> None:
        self._append_inputs(Path(item) for item in filedialog.askopenfilenames(title="添加文本文件"))

    def _add_text_dir(self) -> None:
        selected = filedialog.askdirectory(title="添加文本目录")
        if selected:
            self._append_inputs([Path(selected)])

    def _add_extra_file(self) -> None:
        selected = filedialog.askopenfilename(title="选择额外字符文件")
        if selected:
            path = Path(selected).expanduser().resolve()
            if path not in self.extra_character_files:
                self.extra_character_files.append(path)
                self._write_log(f"已添加额外字符文件：{path}")

    def _append_inputs(self, paths) -> None:
        for path in paths:
            resolved = path.expanduser().resolve()
            if resolved not in self.text_inputs:
                self.text_inputs.append(resolved)
                self.input_list.insert(tk.END, str(resolved))

    def _remove_selected(self) -> None:
        for index in reversed(self.input_list.curselection()):
            self.input_list.delete(index)
            del self.text_inputs[index]

    def _clear_inputs(self) -> None:
        self.text_inputs.clear()
        self.input_list.delete(0, tk.END)

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.analyze_button.configure(state=state)
        self.build_button.configure(state=state)

    def _write_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert(tk.END, text.rstrip() + "\n")
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def _request(self, analyze_only: bool) -> BuildRequest:
        font = self.font_var.get().strip()
        if not font:
            raise ValueError("请选择完整源字体")
        if not self.text_inputs:
            raise ValueError("请至少添加一个文本文件或目录")
        output = self.output_var.get().strip()
        if not analyze_only and not output:
            raise ValueError("请选择输出字体路径")
        report = self.report_var.get().strip()
        safe_set = self.safe_set_var.get()
        return BuildRequest(
            source_font=Path(font), text_inputs=list(self.text_inputs),
            output_font=None if analyze_only else Path(output), report_path=Path(report) if report else None,
            analyze_only=analyze_only, profile=self.profile_var.get(),
            extra_character_files=list(self.extra_character_files), extra_characters=self.extra_chars_var.get(),
            safe_set=None if safe_set == "自动" else safe_set,
            retain_gids=self.retain_gids_var.get(), allow_missing=self.allow_missing_var.get(),
        )

    def _start(self, analyze_only: bool) -> None:
        try:
            request = self._request(analyze_only)
        except ValueError as exc:
            messagebox.showerror("参数不完整", str(exc), parent=self.master)
            return
        self._set_busy(True)
        self.status_var.set("正在分析…" if analyze_only else "正在生成…")
        self._write_log("—" * 48)
        self._write_log(self.status_var.get())

        def worker() -> None:
            try:
                report = execute(request)
            except (ValueError, TextScanError, FontBuildError, OSError) as exc:
                self._results.put(("error", str(exc)))
                return
            self._results.put(("success", (report, analyze_only)))

        threading.Thread(target=worker, name="wc4-font-builder", daemon=True).start()
        self.master.after(50, self._poll_results)

    def _poll_results(self) -> None:
        try:
            kind, payload = self._results.get_nowait()
        except queue.Empty:
            self.master.after(50, self._poll_results)
            return
        if kind == "error":
            self._finish_error(str(payload))
            return
        report, analyze_only = payload
        self._finish_success(report, bool(analyze_only))

    def _finish_error(self, detail: str) -> None:
        self._set_busy(False)
        self.status_var.set("失败")
        self._write_log(f"失败：{detail}")
        messagebox.showerror("处理失败", detail, parent=self.master)

    def _finish_success(self, report: AnalysisReport | BuildReport, analyze_only: bool) -> None:
        self._set_busy(False)
        self.status_var.set("完成")
        title = "覆盖分析完成" if analyze_only else "字体生成完成"
        text = _summary(report)
        self._write_log(text)
        if isinstance(report, BuildReport):
            self._write_log(f"输出：{report.outputFont}")
        messagebox.showinfo(title, text, parent=self.master)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in args:
        root = tk.Tk()
        root.withdraw()
        FontBuilderApp(root)
        root.update_idletasks()
        root.destroy()
        return 0
    root = tk.Tk()
    FontBuilderApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
