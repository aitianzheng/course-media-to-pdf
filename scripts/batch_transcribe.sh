#!/usr/bin/env bash
set -u

usage() {
  echo "Usage: $0 --input DIR --output DIR [--model MODEL] [--backend auto|cpu|metal] [--ffmpeg PATH]"
}

SRC=""
DEST=""
MODEL="qwen3-asr-0.6b"
BACKEND="auto"
FFMPEG="$(command -v ffmpeg 2>/dev/null || true)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --input|-i) SRC="$2"; shift 2 ;;
    --output|-o) DEST="$2"; shift 2 ;;
    --model|-m) MODEL="$2"; shift 2 ;;
    --backend) BACKEND="$2"; shift 2 ;;
    --ffmpeg) FFMPEG="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$SRC" || -z "$DEST" || ! -d "$SRC" ]]; then
  usage >&2
  exit 2
fi
if ! command -v openasr >/dev/null 2>&1; then
  echo "openasr is not on PATH" >&2
  exit 1
fi
if [[ -z "$FFMPEG" || ! -x "$FFMPEG" ]]; then
  echo "ffmpeg is required; pass --ffmpeg PATH" >&2
  exit 1
fi

mkdir -p "$DEST"
LOG="$DEST/_transcription.log"
touch "$LOG"

find "$SRC" -type f \( \
  -iname '*.mp4' -o -iname '*.mov' -o -iname '*.mkv' -o -iname '*.webm' \
  -o -iname '*.m4v' -o -iname '*.avi' -o -iname '*.mp3' -o -iname '*.m4a' \
  -o -iname '*.wav' -o -iname '*.aac' -o -iname '*.flac' -o -iname '*.ogg' -o -iname '*.opus' \
\) -print0 | while IFS= read -r -d '' file; do
  rel="${file#"$SRC"/}"
  out="$DEST/${rel%.*}.txt"
  mkdir -p "$(dirname "$out")"
  if [[ -s "$out" ]]; then
    echo "SKIP $rel" >> "$LOG"
    continue
  fi
  echo "START $rel" | tee -a "$LOG"
  if [[ "$BACKEND" == "auto" ]]; then
    openasr transcribe "$file" --model "$MODEL" --format text --ffmpeg-bin "$FFMPEG" --output "$out" >> "$LOG" 2>&1
  else
    OPENASR_GGML_BACKEND="$BACKEND" openasr transcribe "$file" --model "$MODEL" --format text --ffmpeg-bin "$FFMPEG" --output "$out" >> "$LOG" 2>&1
  fi
  status=$?
  if [[ $status -eq 0 && -s "$out" ]]; then
    echo "DONE $rel" | tee -a "$LOG"
  else
    echo "ERROR $rel status=$status" | tee -a "$LOG"
    rm -f "$out"
  fi
done

echo "BATCH_FINISHED" | tee -a "$LOG"
