---
name: course-media-to-pdf
description: Convert a local folder of video or audio lessons into a structured Chinese transcript set and a polished, searchable PDF tutorial with section/chapter TOC. Use when the user asks to batch transcribe course media, clean the wording, or package lessons into a book-like document.
---

# Course Media to PDF

Turn a local course library into a reusable learning document while keeping the original media untouched.

## Output contract

Produce, unless the user requests otherwise:

- a transcript directory that mirrors the source directory tree;
- a separate polished-transcript directory, never an in-place overwrite;
- one A4 PDF with cover, section hierarchy, a 42-or-whatever-count chapter TOC, page numbers, searchable text, and chapter content;
- a log containing input count, completed count, failures, model/backend, and output locations.

Use stable, descriptive output names. Put generated deliverables under the workspace or the user-requested output directory. Do not copy large media into the skill folder.

## Workflow

1. Inspect the source directory before changing anything. Count supported media, identify section directories, and report the planned output location. Preserve filenames and relative paths. Do not modify or delete source media.
2. Preflight `openasr`, `ffmpeg`, Python with `reportlab`/`pypdf`, a Chinese-capable TrueType font, and `pdftoppm`. If a required dependency is missing, explain the install or approval needed before starting a long job.
3. Batch-transcribe with `scripts/batch_transcribe.sh`. It resumes by skipping non-empty existing outputs, writes one text file per media file, preserves nested directories, and continues after per-file errors.
4. Choose the model according to the machine and user priority. For Chinese course speech, prefer `qwen3-asr-0.6b` as the safe local default; use `qwen3-asr-1.7b` when memory permits. On Apple Silicon machines, if Metal reports out-of-memory, rerun the 1.7B model with `--backend cpu` or fall back to 0.6B. Never silently switch to a cloud transcription service.
5. Only polish when requested. Run `scripts/polish_transcripts.py` into a new directory. Its cleanup must be conservative: remove hesitation fillers and accidental adjacent duplication, normalize punctuation and paragraph breaks, and preserve order, claims, examples, numbers, names, and uncertainty. Do not invent missing content or silently fact-check/rewrite claims.
6. Build the PDF with `scripts/build_course_pdf.py`. For PDF authoring, follow the available PDF skill: mark the artifact operation, use ReportLab, include a TOC generated from actual headings, and keep the final PDF under `output/pdf/` unless the user chooses another path.
7. Validate before delivery: compare source/media/text counts, check non-empty outputs and zero unexplained errors, reopen the PDF with `pypdf`, verify representative chapter titles and text, render representative first/TOC/content/final pages with `pdftoppm`, and inspect for missing Chinese glyphs, clipping, overlaps, blank pages, or broken page numbers. Regenerate if QA finds a defect.

## Important boundaries

- A transcript is not a verified manuscript. Tell the user that proper nouns, numbers, and ASR ambiguities may need audio review.
- Keep raw and polished text separate so the user can compare them.
- Long batch jobs must be resumable. Never make the user restart completed files after an interruption.
- Do not create summaries, teaching explanations, or new claims unless the user asks for them. This skill's default deliverable is a faithful, readable course transcript assembled as a PDF.

## Helpers

- Read `references/usage.md` when choosing commands, models, or output layouts.
- Run `scripts/batch_transcribe.sh` for media-to-text.
- Run `scripts/polish_transcripts.py` for conservative wording cleanup.
- Run `scripts/build_course_pdf.py` for the final searchable PDF.
