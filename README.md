<p align="center">
  <a href="README.md">🇨🇳 中文</a>
  <span> · </span>
  <a href="README.en.md">🇬🇧 English</a>
</p>

# 课程媒体转 PDF

将本地学习视频、音频课程批量转换为文字，进行保守润色，并整理成带章节目录、页码和可搜索文本的 PDF 教程。

## 功能

- 递归扫描本地视频和音频文件。
- 使用本地 OpenASR 推理，脚本不会将媒体上传到云端。
- 支持 `qwen3-asr-0.6b` 和 `qwen3-asr-1.7b` 等 OpenASR 模型。
- 支持断点续跑：已有的非空文本文件会自动跳过。
- 保留原始目录结构，输出一一对应的 `.txt` 文件和处理日志。
- 可选的保守润色：清理口语填充、重复表达、断句和标点，不主动改写观点。
- 生成 A4 PDF，包含封面、分部标题、章节目录、页码和可搜索正文。
- 生成 PDF 前可以检查文本数量、PDF 页数、中文字体和页面渲染结果。

## 工作流程

```text
视频 / 音频
    ↓
OpenASR 批量转写
    ↓
原始文本
    ↓（可选）
保守润色
    ↓
带目录的 PDF 教程
```

## 环境要求

- macOS、Linux 或其他能够运行 Bash 的环境。
- Python 3.9 或更高版本。
- 已安装并可在 `PATH` 中找到的 `openasr` 命令。
- `ffmpeg`，用于读取视频或音频中的声音。
- Python 包：`reportlab`、`pypdf`。
- 支持中文的 TrueType 字体。macOS 默认使用：`/System/Library/Fonts/STHeiti Medium.ttc`。
- 可选：`pdftoppm`，用于生成页面图片进行视觉检查。

安装 Python 依赖：

```bash
python3 -m pip install reportlab pypdf
```

请先按照 OpenASR 项目的说明安装 OpenASR CLI，并确认：

```bash
openasr --help
ffmpeg -version
```

## 输入目录结构

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

## 快速开始

### 1. 批量转写

使用安全的默认模型：

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts" \
  --model qwen3-asr-0.6b
```

使用更大的 1.7B 模型：

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts-1.7b" \
  --model qwen3-asr-1.7b
```

Apple Silicon 如果出现 Metal 显存不足，可以改用 CPU：

```bash
course-media-to-pdf/scripts/batch_transcribe.sh \
  --input "/path/to/course-media" \
  --output "/path/to/course-transcripts-1.7b-cpu" \
  --model qwen3-asr-1.7b \
  --backend cpu
```

支持的媒体格式包括：`mp4`、`mov`、`mkv`、`webm`、`m4v`、`avi`、`mp3`、`m4a`、`wav`、`aac`、`flac`、`ogg` 和 `opus`。

脚本会在输出目录写入 `_transcription.log`。重新运行同一命令时，会跳过已有的非空文本文件，并继续处理未完成或失败的文件。

### 2. 保守润色文本

润色会写入新的目录，不会覆盖原始转写结果：

```bash
python3 course-media-to-pdf/scripts/polish_transcripts.py \
  --input "/path/to/course-transcripts-1.7b-cpu" \
  --output "/path/to/course-transcripts-1.7b-cpu-polished"
```

默认只处理口语层面的明显问题，包括停顿词、相邻重复、重复标点和过长段落。它不会主动补充事实、修改观点或核验专有名词、数字。

### 3. 生成 PDF

```bash
python3 course-media-to-pdf/scripts/build_course_pdf.py \
  --input "/path/to/course-transcripts-1.7b-cpu-polished" \
  --output "/path/to/output/course-tutorial.pdf" \
  --title "课程全文教程"
```

如果系统没有默认中文字体，可以指定字体：

```bash
python3 course-media-to-pdf/scripts/build_course_pdf.py \
  --input "/path/to/course-transcripts-1.7b-cpu-polished" \
  --output "/path/to/output/course-tutorial.pdf" \
  --title "课程全文教程" \
  --font "/path/to/your/chinese-font.ttc"
```

## 输出结果

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

原始文本和润色文本应当保留在不同目录中，方便回查 ASR 结果。PDF 是可搜索文本，不是图片扫描件。

## 命令参数

### `batch_transcribe.sh`

| 参数 | 说明 |
|---|---|
| `--input`, `-i` | 输入媒体目录 |
| `--output`, `-o` | 文本输出目录 |
| `--model`, `-m` | OpenASR 模型，默认 `qwen3-asr-0.6b` |
| `--backend` | `auto`、`cpu` 或 `metal`，默认 `auto` |
| `--ffmpeg` | `ffmpeg` 可执行文件路径 |

### `build_course_pdf.py`

| 参数 | 说明 |
|---|---|
| `--input` | 包含分部目录和 `.txt` 文件的目录 |
| `--output` | PDF 输出路径 |
| `--title` | PDF 标题 |
| `--font` | 中文 TrueType 字体路径 |
| `--date` | 可选的封面日期 |

## 在 Codex 与 Claude Code 中使用

### 安装 Skill

请克隆整个仓库；不要只复制 `SKILL.md`，因为批处理脚本和参考文档也需要保留。

Codex 用户级安装：

```bash
git clone https://github.com/aitianzheng/course-media-to-pdf.git \
  ~/.agents/skills/course-media-to-pdf
```

也可以将仓库放在当前项目的 `.agents/skills/course-media-to-pdf/`，使它只对该项目可用。启动或刷新 Codex 后，运行 `/skills` 查看可用 Skill，并用 `$course-media-to-pdf` 显式调用；也可以直接描述任务，让 Codex 根据 `SKILL.md` 的 `description` 自动选择。

Claude Code 用户级安装：

```bash
git clone https://github.com/aitianzheng/course-media-to-pdf.git \
  ~/.claude/skills/course-media-to-pdf
```

如果只想在某个项目中使用，可放在该项目的 `.claude/skills/course-media-to-pdf/`。在 Claude Code 中输入 `/course-media-to-pdf` 可显式调用，也可以直接描述批量转写和生成 PDF 的需求，让 Claude Code 根据 Skill 的 `description` 自动加载。

Claude Code 使用 Skill 目录名作为斜杠命令名，因此目录名应保持为 `course-media-to-pdf`。

### 调用示例

Codex：

```text
$course-media-to-pdf
请处理 /path/to/course-media 下的全部视频和音频，使用 qwen3-asr-1.7b；完成保守润色，并生成带章节目录的可搜索 PDF。
```

Claude Code：

```text
/course-media-to-pdf
请处理 /path/to/course-media 下的全部视频和音频，使用 qwen3-asr-1.7b；完成保守润色，并生成带章节目录的可搜索 PDF。
```

无论使用哪种 Agent，都需要先完成本机依赖安装，并确保 `openasr`、`ffmpeg`、Python 的 `reportlab` 和 `pypdf` 可用。Skill 只编排本地命令，不会自动上传媒体文件。

## 项目结构

```text
course-media-to-pdf/
├── SKILL.md                         # Skill 说明
├── README.md                        # 中文说明（默认入口）
├── README.en.md                     # 英文说明
├── agents/openai.yaml               # Codex 界面元数据
├── references/usage.md              # 命令参考
└── scripts/
    ├── batch_transcribe.sh          # 视频/音频 → TXT
    ├── polish_transcripts.py        # 保守文字清理
    └── build_course_pdf.py          # TXT → 可搜索 PDF
```

## 故障排查

### `openasr is not on PATH`

确认 OpenASR CLI 已安装，并将其所在目录加入 `PATH`：

```bash
command -v openasr
openasr --help
```

### `ffmpeg is required`

安装 `ffmpeg`，或通过 `--ffmpeg` 明确指定可执行文件路径。

### 1.7B 模型出现显存不足

在 Apple Silicon 上使用：

```bash
--backend cpu
```

如果 CPU 转写速度无法接受，可以改用 `qwen3-asr-0.6b`，或者拆分课程后分批处理。

### PDF 中文显示异常

使用支持中文的字体并传入 `--font`。生成后建议使用 `pdftoppm` 将封面、目录、正文和末页渲染成 PNG，检查字体、分页、页码和是否有空白页。

## 隐私与准确性

- 提供的脚本只处理本地文件，不会自动把媒体上传到云端。
- ASR 结果不是人工校对稿。专有名词、人名、数字、金额和行业术语应结合原音复核。
- “润色”是保守的可读性处理，不等于事实核查、编辑改写或课程内容总结。
- 请确保你拥有待处理视频、音频及其文字内容的使用权。

## 许可证

本项目采用 MIT License，详见仓库根目录下的 `LICENSE` 文件。
