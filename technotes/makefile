#!/bin/sh

SRC_FILES = \
    meta.md \
    motivation.md \
    decision_focus.md \
    evaluation_model.md \
    diversity_maintenance.md \
    archive.md \
    selection.md \
    parallelism.md #\
    #api_summary.md

all:
	cat $(SRC_FILES) > report.md
	pandoc report.md -o report.docx
