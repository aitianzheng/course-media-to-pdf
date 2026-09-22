# Usage reference

## Batch transcription

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts" \
  --model qwen3-asr-0.6b
```

For a larger model on a memory-constrained Apple Silicon machine:

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts" \
  --model qwen3-asr-1.7b \
  --backend cpu
```

The command writes `_transcription.log` in the output root. Re-running it skips non-empty `.txt` files and retries failed files.

## Conservative polishing

```bash
python3 course-media-to-pdf/scripts/polish_transcripts.py \
  --input "/path/to/course-transcripts" \
  --output "/path/to/course-transcripts-polished"
```

## PDF packaging

```bash
python3 course-media-to-pdf/scripts/build_course_pdf.py \
  --input "/path/to/course-transcripts-polished" \
  --output "/path/to/output/pdf/course-tutorial.pdf" \
  --title "课程全文教程"
```

Use a Chinese TrueType font with `--font` when the system default is not available. The builder ignores `_transcription.log`, keeps section directories in their natural numeric order, and creates a searchable TOC.
