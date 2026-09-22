#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, HRFlowable, PageBreak, PageTemplate, Paragraph, Spacer
from reportlab.platypus.tableofcontents import TableOfContents


def natural_key(path: Path):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', path.name)]


def section_key(path: Path):
    order = {'前言': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5}
    match = re.match(r'([一二三四五六七八九十]+)、', path.name)
    return (order.get(match.group(1), 99) if match else 99, path.name)


def chunks(text: str):
    text = re.sub(r'\s+', ' ', text.replace('\ufeff', '').strip())
    sentences = re.split(r'(?<=[。！？!?；])', text)
    out, buf = [], ''
    for sentence in sentences:
        if not sentence:
            continue
        if buf and len(buf) + len(sentence) > 420:
            out.append(buf.strip())
            buf = ''
        buf += sentence
    if buf.strip():
        out.append(buf.strip())
    return out


class CourseDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='normal')
        self.addPageTemplates([PageTemplate(id='course', frames=[frame], onPage=draw_page)])

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            if flowable.style.name == 'SectionTitle':
                self.notify('TOCEntry', (0, flowable.getPlainText(), self.page))
            elif flowable.style.name == 'ChapterTitle':
                self.notify('TOCEntry', (1, flowable.getPlainText(), self.page))


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setStrokeColor(colors.HexColor('#D9D2C3'))
        canvas.setLineWidth(0.4)
        canvas.line(doc.leftMargin, height - 14 * mm, width - doc.rightMargin, height - 14 * mm)
        canvas.setFont('CourseFont', 8.5)
        canvas.setFillColor(colors.HexColor('#746B60'))
        canvas.drawString(doc.leftMargin, height - 10 * mm, doc.title or '课程整理稿')
        canvas.drawRightString(width - doc.rightMargin, 10 * mm, f'第 {page} 页')
        canvas.line(doc.leftMargin, 14 * mm, width - doc.rightMargin, 14 * mm)
    canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(name='CoverKicker', parent=base['Normal'], fontName='CourseFont', fontSize=12, leading=18, textColor=colors.HexColor('#8B7355'), alignment=TA_CENTER, spaceAfter=18))
    base.add(ParagraphStyle(name='CoverTitle', parent=base['Title'], fontName='CourseFont', fontSize=30, leading=40, textColor=colors.HexColor('#2B2926'), alignment=TA_CENTER, spaceAfter=18))
    base.add(ParagraphStyle(name='CoverSubtitle', parent=base['Normal'], fontName='CourseFont', fontSize=12, leading=20, textColor=colors.HexColor('#5C554C'), alignment=TA_CENTER))
    base.add(ParagraphStyle(name='SectionTitle', parent=base['Heading1'], fontName='CourseFont', fontSize=20, leading=28, textColor=colors.HexColor('#2F4A43'), spaceBefore=8, spaceAfter=12, keepWithNext=True))
    base.add(ParagraphStyle(name='ChapterTitle', parent=base['Heading2'], fontName='CourseFont', fontSize=15, leading=24, textColor=colors.HexColor('#8C4F38'), spaceBefore=12, spaceAfter=9, keepWithNext=True))
    base.add(ParagraphStyle(name='BodyCN', parent=base['BodyText'], fontName='CourseFont', fontSize=10.5, leading=19, textColor=colors.HexColor('#302E2B'), firstLineIndent=21, alignment=TA_LEFT, wordWrap='CJK', spaceAfter=8))
    base.add(ParagraphStyle(name='Meta', parent=base['Normal'], fontName='CourseFont', fontSize=8.5, leading=14, textColor=colors.HexColor('#81796D'), wordWrap='CJK', spaceAfter=10))
    base.add(ParagraphStyle(name='TOCHeading', parent=base['Heading1'], fontName='CourseFont', fontSize=22, leading=30, textColor=colors.HexColor('#2F4A43'), spaceAfter=18))
    base.add(ParagraphStyle(name='TOCLevel0', parent=base['Normal'], fontName='CourseFont', fontSize=11.5, leading=20, leftIndent=0, textColor=colors.HexColor('#2F4A43'), spaceBefore=5))
    base.add(ParagraphStyle(name='TOCLevel1', parent=base['Normal'], fontName='CourseFont', fontSize=9.5, leading=17, leftIndent=16, textColor=colors.HexColor('#554E46')))
    return base


def main():
    parser = argparse.ArgumentParser(description='Build a searchable Chinese course PDF from organized text files.')
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--title', default='课程全文教程')
    parser.add_argument('--font', type=Path, default=Path('/System/Library/Fonts/STHeiti Medium.ttc'))
    parser.add_argument('--date', default='')
    args = parser.parse_args()
    if not args.input.is_dir():
        raise SystemExit(f'input directory does not exist: {args.input}')
    if not args.font.exists():
        raise SystemExit(f'Chinese font does not exist: {args.font}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont('CourseFont', str(args.font), subfontIndex=0))
    st = styles()

    sections = []
    for directory in sorted((p for p in args.input.iterdir() if p.is_dir()), key=section_key):
        files = sorted((p for p in directory.glob('*.txt') if not p.name.startswith('_')), key=natural_key)
        if files:
            sections.append((directory.name, files))
    count = sum(len(files) for _, files in sections)
    if not count:
        raise SystemExit('no chapter text files found')

    doc = CourseDocTemplate(str(args.output), pagesize=A4, leftMargin=21 * mm, rightMargin=21 * mm, topMargin=21 * mm, bottomMargin=21 * mm, title=args.title, author='Codex', subject=f'{count}章节课程教程')
    story = [Spacer(1, 35 * mm), Paragraph('课程全文润色稿', st['CoverKicker']), Paragraph(escape(args.title), st['CoverTitle']), Paragraph(f'{count} 个章节 · 转写整理编排版', st['CoverSubtitle']), Spacer(1, 18 * mm), HRFlowable(width='42%', thickness=1.2, color=colors.HexColor('#B08B63'), hAlign='CENTER'), Spacer(1, 18 * mm), Paragraph('正文按章节整理，保留原始内容顺序，并对口语填充、重复表达、断句和标点进行保守处理。专有名词、数字和语音识别结果仍建议结合原声核对。', st['CoverSubtitle']), Spacer(1, 20 * mm)]
    if args.date:
        story.append(Paragraph(escape(args.date), st['CoverSubtitle']))
    story.extend([PageBreak(), Paragraph('目录', st['TOCHeading'])])
    toc = TableOfContents()
    toc.levelStyles = [st['TOCLevel0'], st['TOCLevel1']]
    toc.dotsMinLevel = 0
    story.extend([toc, PageBreak()])

    chapter_no = 0
    for section_name, files in sections:
        story.extend([Paragraph(escape(section_name), st['SectionTitle']), HRFlowable(width='100%', thickness=0.7, color=colors.HexColor('#D9D2C3')), Spacer(1, 7)])
        for file_path in files:
            chapter_no += 1
            title = file_path.stem
            story.append(Paragraph(escape(f'{chapter_no}. {title}'), st['ChapterTitle']))
            story.append(Paragraph(escape(f'所属部分：{section_name}　|　来源：{file_path.name}'), st['Meta']))
            for chunk in chunks(file_path.read_text(encoding='utf-8', errors='replace')):
                story.append(Paragraph(escape(chunk), st['BodyCN']))
            story.append(Spacer(1, 5))
        story.append(PageBreak())
    doc.multiBuild(story)
    print(f'created {args.output} with {chapter_no} chapters')


if __name__ == '__main__':
    main()
