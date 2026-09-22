# 课程媒体转 PDF教程 / Course Media to PDF

将本地学习视频、音频课程批量转换为文字，进行保守润色，并整理成带章节目录、页码和可搜索文本的 PDF 教程。

Batch-transcribe local video and audio courses, conservatively polish the transcripts, and package them into a searchable PDF tutorial with a chapter table of contents and page numbers.

## 功能特性 / Features

- 支持递归扫描本地视频和音频文件。 / Recursively scans local video and audio files.
- 使用本地 OpenASR 推理，不会通过这些脚本将媒体上传到云端。 / Uses local OpenASR inference; the provided scripts do not upload media to a cloud service.
- 支持 `qwen3-asr-0.6b` 和 `qwen3-asr-1.7b` 等 OpenASR 模型。 / Supports OpenASR models such as `qwen3-asr-0.6b` and `qwen3-asr-1.7b`.
- 支持断点续跑：已有的非空文本文件会自动跳过。 / Resumes safely by skipping existing non-empty transcript files.
- 保留原始目录结构，输出一一对应的 `.txt` 文件和处理日志。 / Preserves the source tree and writes matching `.txt` files plus a log.
- 可选的保守润色：清理口语填充、重复表达、断句和标点，不主动改写观点。 / Optionally cleans fillers, adjacent repetition, sentence breaks, and punctuation without rewriting claims.
- 生成 A4 PDF，包含封面、分部标题、章节目录、页码和可搜索正文。 / Builds an A4 PDF with a cover, section headings, chapter TOC, page numbers, and searchable text.
- 在生成 PDF 前可以检查文本数量、PDF 页数、中文字体和页面渲染结果。 / Supports pre-delivery checks for transcript counts, PDF pages, Chinese glyphs, and rendered pages.

## 工作流程 / Workflow

```text
视频 / 音频
    ↓
OpenASR 批量转写 / Batch transcription
    ↓
原始文本 / Raw transcripts
    ↓（可选 / optional）
保守润色 / Conservative polishing
    ↓
带目录的 PDF 教程 / Searchable PDF tutorial
```

## 环境要求 / Requirements

- macOS、Linux 或其他能够运行 Bash 的环境。 / macOS, Linux, or another Bash-capable environment.
- Python 3.9+。
- 已安装并可在 `PATH` 中找到的 `openasr` 命令。 / The `openasr` command installed and available on `PATH`.
- `ffmpeg`，用于从视频或音频中读取声音。 / `ffmpeg` for extracting or reading media audio.
- Python 包：`reportlab`、`pypdf`。 / Python packages: `reportlab` and `pypdf`.
- 一个支持中文的 TrueType 字体。macOS 默认使用：`/System/Library/Fonts/STHeiti Medium.ttc`。 / A Chinese-capable TrueType font; macOS defaults to `/System/Library/Fonts/STHeiti Medium.ttc`.
- 可选：`pdftoppm`，用于生成页面图片进行视觉检查。 / Optional: `pdftoppm` for visual PDF checks.

安装 Python 依赖 / Install Python dependencies:

```bash
python3 -m pip install reportlab pypdf
```

请先按照 OpenASR 项目的说明安装 OpenASR CLI，并确认 / Install the OpenASR CLI according to its project documentation, then verify:

```bash
openasr --help
ffmpeg -version
```

## 输入目录结构 / Input Layout

建议将课程按照“分部 / 章节”组织：

```text
course-media/
├── 一、基础理论/
│   ├── 01-第一课.mp4
│   └── 02-第二课.mp3
└── 二、实战方法/
    ├── 01-案例一.mov
    └── 02-案例二.m4a
```

PDF 生成器会读取输入目录下的分部目录，并按照目录名和文件名中的数字自然排序。建议不要把章节文本直接放在输入根目录下。

The PDF builder expects section directories directly under the input directory. Chapter text files should be inside those section directories so that the section hierarchy can be preserved.

## 快速开始 / Quick Start

### 1. 批量转写 / Batch transcribe

使用安全的默认模型 / Use the safer default model:

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts" \
  --model qwen3-asr-0.6b
```

使用更大的 1.7B 模型 / Use the larger 1.7B model:

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts-1.7b" \
  --model qwen3-asr-1.7b
```

Apple Silicon 如果出现 Metal 显存不足，可以改用 CPU。 / If Metal runs out of memory on Apple Silicon, use the CPU backend:

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts-1.7b-cpu" \
  --model qwen3-asr-1.7b \
  --backend cpu
```

支持的视频和音频格式包括：`mp4`、`mov`、`mkv`、`webm`、`m4v`、`avi`、`mp3`、`m4a`、`wav`、`aac`、`flac`、`ogg` 和 `opus`。 / Supported extensions include `mp4`, `mov`, `mkv`, `webm`, `m4v`, `avi`, `mp3`, `m4a`, `wav`, `aac`, `flac`, `ogg`, and `opus`.

脚本会在输出目录写入 `_transcription.log`。重新运行同一命令时，会跳过已有的非空文本文件，并继续处理未完成或失败的文件。 / The script writes `_transcription.log` to the output directory. Re-running the same command skips non-empty transcripts and continues unfinished or failed files.

### 2. 保守润色 / Conservatively polish transcripts

润色会写入新的目录，不会覆盖原始转写结果。 / Polishing writes to a new directory and never overwrites the raw transcripts:

```bash
python3 course-media-to-pdf/scripts/polish_transcripts.py \
  --input "/path/to/course-transcripts-1.7b-cpu" \
  --output "/path/to/course-transcripts-1.7b-cpu-polished"
```

默认只处理口语层面的明显问题，包括停顿词、相邻重复、重复标点和过长段落。它不会主动补充事实、修改观点或核验专有名词、数字。 / It only addresses obvious speech-level issues such as fillers, adjacent repetition, duplicated punctuation, and oversized paragraphs. It does not add facts, change claims, or verify proper names and numbers.

### 3. 生成 PDF / Build the PDF

```bash
python3 course-media-to-pdf/scripts/build_course_pdf.py \
  --input "/path/to/course-transcripts-1.7b-cpu-polished" \
  --output "/path/to/output/course-tutorial.pdf" \
  --title "课程全文教程"
```

如果系统没有默认中文字体，可以指定字体。 / If the default Chinese font is unavailable, specify one explicitly:

```bash
python3 course-media-to-pdf/scripts/build_course_pdf.py \
  --input "/path/to/course-transcripts-1.7b-cpu-polished" \
  --output "/path/to/output/course-tutorial.pdf" \
  --title "Course Tutorial" \
  --font "/path/to/your/chinese-font.ttc"
```

## 输出结果 / Outputs

典型输出结构：

```text
course-transcripts/
├── 一、基础理论/
│   ├── 01-第一课.txt
│   └── 02-第二课.txt
└── _transcription.log

course-transcripts-polished/
├── 一、基础理论/
│   ├── 01-第一课.txt
│   └── 02-第二课.txt

output/
└── course-tutorial.pdf
```

原始文本和润色文本应当保留在不同目录中，方便回查 ASR 结果。PDF 是可搜索文本，不是图片扫描件。 / Keep raw and polished transcripts in separate directories for review. The PDF contains searchable text rather than scanned page images.

Raw and polished transcripts are intentionally kept separate. This makes it possible to compare edits and review uncertain names, numbers, or terminology against the original audio.

## 命令参数 / CLI Options

### `batch_transcribe.sh`

| 参数 / Option | 说明 / Description |
|---|---|
| `--input`, `-i` | 输入媒体目录 / Input media directory |
| `--output`, `-o` | 文本输出目录 / Transcript output directory |
| `--model`, `-m` | OpenASR 模型，默认 `qwen3-asr-0.6b` / OpenASR model; defaults to `qwen3-asr-0.6b` |
| `--backend` | `auto`、`cpu` 或 `metal`，默认 `auto` / `auto`, `cpu`, or `metal`; defaults to `auto` |
| `--ffmpeg` | `ffmpeg` 可执行文件路径 / Path to the `ffmpeg` executable |

### `build_course_pdf.py`

| 参数 / Option | 说明 / Description |
|---|---|
| `--input` | 包含分部目录和 `.txt` 文件的目录 / Directory containing section folders and `.txt` files |
| `--output` | PDF 输出路径 / PDF output path |
| `--title` | PDF 标题 / PDF title |
| `--font` | 中文 TrueType 字体路径 / Chinese TrueType font path |
| `--date` | 可选的封面日期 / Optional cover date |

## 项目结构 / Project Structure

```text
course-media-to-pdf/
├── SKILL.md                         # Codex skill instructions
├── README.md                        # This bilingual README
├── agents/openai.yaml               # Codex UI metadata
├── references/usage.md              # Command reference
└── scripts/
    ├── batch_transcribe.sh          # Video/audio → TXT
    ├── polish_transcripts.py        # Conservative text cleanup
    └── build_course_pdf.py          # TXT → searchable PDF
```

## 故障排查 / Troubleshooting

### `openasr is not on PATH`

确认 OpenASR CLI 已安装，并将其所在目录加入 `PATH`。 / Confirm that the OpenASR CLI is installed and add its directory to `PATH`:

```bash
command -v openasr
openasr --help
```

### `ffmpeg is required`

安装 `ffmpeg`，或通过 `--ffmpeg` 明确指定可执行文件路径。 / Install `ffmpeg`, or pass its executable path with `--ffmpeg`.

### 1.7B 模型出现显存不足

在 Apple Silicon 上使用 / Use this on Apple Silicon:

```bash
--backend cpu
```

如果 CPU 转写速度无法接受，可以改用 `qwen3-asr-0.6b`，或者拆分课程后分批处理。 / If CPU transcription is too slow, use `qwen3-asr-0.6b` or split the course into smaller batches.

### PDF 中文显示异常

使用支持中文的字体并传入 `--font`。生成后建议使用 `pdftoppm` 将封面、目录、正文和末页渲染成 PNG 检查字体、分页、页码和是否有空白页。 / Use a Chinese-capable font with `--font`, then render representative pages with `pdftoppm` to check glyphs, pagination, page numbers, and blank pages.

## 隐私与准确性 / Privacy and Accuracy

- 提供的脚本只处理本地文件；不会自动把媒体上传到云端。 / The provided scripts process local files and do not automatically upload media to the cloud.
- ASR 结果不是人工校对稿。专有名词、人名、数字、金额和行业术语应结合原音复核。 / ASR output is not a human-verified manuscript; review names, numbers, amounts, and technical terms against the audio.
- “润色”是保守的可读性处理，不等于事实核查、编辑改写或课程内容总结。 / “Polishing” is conservative readability cleanup, not fact-checking, editorial rewriting, or course summarization.
- 请确保你拥有待处理视频、音频及其文字内容的使用权。 / Make sure you have the right to process and publish the source media and transcripts.

The scripts are designed for local processing, but transcription quality still depends on the recording, speaker, language, and model. Always review important passages against the original media before publishing or making decisions based on them.

## License / 许可证

本项目暂未指定许可证。公开发布到 GitHub 前，请根据你的使用场景选择并添加合适的 LICENSE 文件，例如 MIT、Apache-2.0 或 GPL-3.0。 / No license is selected yet. Before publishing to GitHub, choose and add an appropriate LICENSE file, such as MIT, Apache-2.0, or GPL-3.0.
