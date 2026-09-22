<p align="center">
  <a href="README.md">🇨🇳 中文</a>
  <span> · </span>
  <a href="README.en.md">🇬🇧 English</a>
</p>

# Course Media to PDF

Batch-transcribe local video and audio courses, conservatively polish the transcripts, and package them into a searchable PDF tutorial with a chapter table of contents and page numbers.

## Features

- Recursively scans local video and audio files.
- Uses local OpenASR inference; the scripts do not upload media to the cloud.
- Supports OpenASR models such as `qwen3-asr-0.6b` and `qwen3-asr-1.7b`.
- Resumes safely by skipping existing non-empty transcript files.
- Preserves the source tree and writes matching `.txt` files plus a processing log.
- Optionally cleans fillers, adjacent repetition, sentence breaks, and punctuation without rewriting claims.
- Builds an A4 PDF with a cover, section headings, chapter table of contents, page numbers, and searchable text.
- Supports pre-delivery checks for transcript counts, PDF pages, Chinese glyphs, and rendered pages.

## Workflow

```text
Video / audio
    ↓
Batch transcription with OpenASR
    ↓
Raw transcripts
    ↓ (optional)
Conservative polishing
    ↓
Searchable PDF tutorial with a table of contents
```

## Requirements

- macOS, Linux, or another Bash-capable environment.
- Python 3.9 or newer.
- The `openasr` command installed and available on `PATH`.
- `ffmpeg` for reading audio from video or audio files.
- Python packages: `reportlab` and `pypdf`.
- A Chinese-capable TrueType font. The default macOS path is `/System/Library/Fonts/STHeiti Medium.ttc`.
- Optional: `pdftoppm` for visual PDF checks.

Install the Python dependencies:

```bash
python3 -m pip install reportlab pypdf
```

Install the OpenASR CLI according to its project documentation, then verify:

```bash
openasr --help
ffmpeg -version
```

## Input Layout

Organize the course as section and chapter directories:

```text
course-media/
├── 1-basics/
│   ├── 01-first-lesson.mp4
│   └── 02-second-lesson.mp3
└── 2-practice/
    ├── 01-case-study.mov
    └── 02-workshop.m4a
```

The PDF builder reads section directories directly under the input directory and sorts section and chapter names naturally by their numbers. Keep chapter text files inside section directories rather than placing them at the input root.

## Quick Start

### 1. Batch transcribe

Use the safer default model:

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts" \
  --model qwen3-asr-0.6b
```

Use the larger 1.7B model:

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts-1.7b" \
  --model qwen3-asr-1.7b
```

On Apple Silicon, use the CPU backend if Metal runs out of memory:

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts-1.7b-cpu" \
  --model qwen3-asr-1.7b \
  --backend cpu
```

Supported media extensions include `mp4`, `mov`, `mkv`, `webm`, `m4v`, `avi`, `mp3`, `m4a`, `wav`, `aac`, `flac`, `ogg`, and `opus`.

The script writes `_transcription.log` to the output directory. Re-running the same command skips non-empty transcripts and continues unfinished or failed files.

### 2. Conservatively polish transcripts

Polishing writes to a new directory and never overwrites the raw transcripts:

```bash
python3 course-media-to-pdf/scripts/polish_transcripts.py \
  --input "/path/to/course-transcripts-1.7b-cpu" \
  --output "/path/to/course-transcripts-1.7b-cpu-polished"
```

The default cleanup addresses obvious speech-level issues such as fillers, adjacent repetition, duplicated punctuation, and oversized paragraphs. It does not add facts, change claims, or verify proper names and numbers.

### 3. Build the PDF

```bash
python3 course-media-to-pdf/scripts/build_course_pdf.py \
  --input "/path/to/course-transcripts-1.7b-cpu-polished" \
  --output "/path/to/output/course-tutorial.pdf" \
  --title "Course Tutorial"
```

If the system does not have a suitable Chinese font, specify one explicitly:

```bash
python3 course-media-to-pdf/scripts/build_course_pdf.py \
  --input "/path/to/course-transcripts-1.7b-cpu-polished" \
  --output "/path/to/output/course-tutorial.pdf" \
  --title "Course Tutorial" \
  --font "/path/to/your/chinese-font.ttc"
```

## Outputs

Typical output layout:

```text
course-transcripts/
├── 1-basics/
│   ├── 01-first-lesson.txt
│   └── 02-second-lesson.txt
└── _transcription.log

course-transcripts-polished/
├── 1-basics/
│   ├── 01-first-lesson.txt
│   └── 02-second-lesson.txt

output/
└── course-tutorial.pdf
```

Keep raw and polished transcripts in separate directories for review. The PDF contains searchable text rather than scanned page images.

## CLI Options

### `batch_transcribe.sh`

| Option | Description |
|---|---|
| `--input`, `-i` | Input media directory |
| `--output`, `-o` | Transcript output directory |
| `--model`, `-m` | OpenASR model; defaults to `qwen3-asr-0.6b` |
| `--backend` | `auto`, `cpu`, or `metal`; defaults to `auto` |
| `--ffmpeg` | Path to the `ffmpeg` executable |

### `build_course_pdf.py`

| Option | Description |
|---|---|
| `--input` | Directory containing section folders and `.txt` files |
| `--output` | PDF output path |
| `--title` | PDF title |
| `--font` | Chinese TrueType font path |
| `--date` | Optional cover date |

## Use in Codex and Claude Code

### Install the skill

Clone the whole repository rather than copying only `SKILL.md`, because the helper scripts and references are part of the skill.

Codex user-level installation:

```bash
git clone https://github.com/aitianzheng/course-media-to-pdf.git \
  ~/.agents/skills/course-media-to-pdf
```

For project-only use, place the repository at `.agents/skills/course-media-to-pdf/`. After starting or refreshing Codex, run `/skills` to inspect available skills and use `$course-media-to-pdf` for explicit invocation. You can also describe the task naturally and let Codex select the skill from the `description` in `SKILL.md`.

Claude Code user-level installation:

```bash
git clone https://github.com/aitianzheng/course-media-to-pdf.git \
  ~/.claude/skills/course-media-to-pdf
```

For project-only use, place it at `.claude/skills/course-media-to-pdf/`. In Claude Code, type `/course-media-to-pdf` to invoke it explicitly, or describe the transcription and PDF task naturally so Claude Code can load it from the skill `description`.

Claude Code derives the slash command from the skill directory name, so keep the directory name as `course-media-to-pdf`.

### Example prompts

Codex:

```text
$course-media-to-pdf
Process all video and audio under /path/to/course-media with qwen3-asr-1.7b, conservatively polish the transcripts, and build a searchable PDF with a chapter table of contents.
```

Claude Code:

```text
/course-media-to-pdf
Process all video and audio under /path/to/course-media with qwen3-asr-1.7b, conservatively polish the transcripts, and build a searchable PDF with a chapter table of contents.
```

With either agent, install the local dependencies first and ensure `openasr`, `ffmpeg`, and Python's `reportlab` and `pypdf` are available. The skill orchestrates local commands and does not automatically upload media files.

## Project Structure

```text
course-media-to-pdf/
├── SKILL.md                         # Skill instructions
├── README.md                        # Chinese documentation (default)
├── README.en.md                     # English documentation
├── agents/openai.yaml               # Codex UI metadata
├── references/usage.md              # Command reference
└── scripts/
    ├── batch_transcribe.sh          # Video/audio → TXT
    ├── polish_transcripts.py        # Conservative text cleanup
    └── build_course_pdf.py          # TXT → searchable PDF
```

## Troubleshooting

### `openasr is not on PATH`

Confirm that the OpenASR CLI is installed and add its directory to `PATH`:

```bash
command -v openasr
openasr --help
```

### `ffmpeg is required`

Install `ffmpeg`, or pass its executable path with `--ffmpeg`.

### The 1.7B model runs out of memory

On Apple Silicon, use:

```bash
--backend cpu
```

If CPU transcription is too slow, use `qwen3-asr-0.6b` or split the course into smaller batches.

### Chinese glyphs look wrong in the PDF

Use a Chinese-capable font with `--font`. After generation, render representative pages with `pdftoppm` to check glyphs, pagination, page numbers, and blank pages.

## Privacy and Accuracy

- The provided scripts process local files and do not automatically upload media to the cloud.
- ASR output is not a human-verified manuscript; review names, numbers, amounts, and technical terms against the audio.
- Polishing is conservative readability cleanup, not fact-checking, editorial rewriting, or course summarization.
- Make sure you have the right to process and publish the source media and transcripts.

## License

This project is licensed under the MIT License. See the `LICENSE` file in the repository root for details.
