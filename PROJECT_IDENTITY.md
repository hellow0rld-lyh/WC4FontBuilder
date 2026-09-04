# WC4 Font Builder — Project Identity

Project-ID: WC4FontBuilder
Product: Text-driven OpenType font subset builder
Status: Active

## Purpose

Generate compact OpenType fonts from a full source font plus the text actually used by a game/mod. The tool owns character discovery, safety-character augmentation, OpenType-aware subsetting, coverage validation, metric preservation checks, and a machine-readable report.

## Boundary

This repository is a standalone support tool. It is not a WC4 gameplay product, SO Variant, clean-room runtime component, or formal cross-repository package dependency. WC4 projects may consume its generated font artifact manually or through a future separately authorized integration.
