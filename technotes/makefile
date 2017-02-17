#!/bin/sh

SRC_FILES = \
    meta.md \
    motivation.md \
    decision_focus.md \
    archive.md \
    diversity_maintenance.md \
    evaluation_model.md \
    selection.md \
    parallelism.md \
    api_summary.md

all:
	cat $(SRC_FILES) > report.md
	pandoc report.md -o report.docx
