#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def polish(text: str) -> str:
    text = text.replace('\ufeff', '').replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s*([，。！？；：、])\s*', r'\1', text)
    text = re.sub(r'([。！？；])\s*([。！？；])+', r'\1', text)
    text = re.sub(r'(^|[。！？；，])\s*(?:嗯|呃|哎|哎呀|呀|哈)(?=[，。！？；])', r'\1', text)
    text = re.sub(r'啊(?=[，。！？；])', '', text)
    text = re.sub(r'呢(?=[，。！？；])', '', text)
    text = re.sub(r'对吧(?=[，。！？；])', '', text)
    for phrase in ['然后', '其实', '就是', '这个', '那个', '所以', '但是', '我们', '很多朋友']:
        text = re.sub(rf'({phrase})[，、 ]*\1', r'\1', text)
    text = re.sub(r'([，。！？；])\1+', r'\1', text)
    text = re.sub(r' {2,}', ' ', text)

    sentences = re.split(r'(?<=[。！？])', text.strip())
    paragraphs, buf = [], ''
    for sentence in sentences:
        if not sentence:
            continue
        if buf and len(buf) + len(sentence) > 360:
            paragraphs.append(buf.strip())
            buf = ''
        buf += sentence
    if buf.strip():
        paragraphs.append(buf.strip())
    return '\n\n'.join(paragraphs) + '\n'


def main():
    parser = argparse.ArgumentParser(description='Conservatively polish ASR transcript text.')
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if not args.input.is_dir():
        raise SystemExit(f'input directory does not exist: {args.input}')
    count = 0
    for source in sorted(args.input.rglob('*.txt')):
        if source.name.startswith('_'):
            continue
        target = args.output / source.relative_to(args.input)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(polish(source.read_text(encoding='utf-8', errors='replace')), encoding='utf-8')
        count += 1
    print(f'polished {count} text files into {args.output}')


if __name__ == '__main__':
    main()
