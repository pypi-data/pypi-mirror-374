# AST transform to slide js.
import sys
from pathlib import Path
from .utils import *
from .slide import *
import re


def remove_html_comments(s: str):
    if s.startswith('<!--'):
        if s.endswith('-->'):
            return s.removeprefix('<!--').removesuffix('-->')
    return None


# @deprecated
def md_to_slides(md_text) -> Slides:
    state = None
    buffer = []
    slides = [] # type: list[Slide]

    def finish_prev_state():
        nonlocal buffer
        nonlocal slides
        nonlocal state
        if state is None or state == 'empty' or state == 'none':
            pass
        elif state == 'slide':
            slides.append(Slide('\n\n'.join(buffer)))
        elif state == 'comment':
            slides[-1].set_comments('\n\n'.join(buffer))
        else:
            assert False, 'Unknown state!'
        buffer = []
        state = None

    while len(md_text := md_text.strip()) > 0:
        m = re.search(r'<!--\s*mode:?\s*(\w+?)\s*-->', md_text)
        next_start = m.start() if m is not None else len(md_text)
        if next_start != 0:
            buffer.append(md_text[:next_start].strip())
            md_text = md_text[next_start:]
            continue
        mode_text = m.group(1)
        if mode_text == 'slide':
            finish_prev_state()
            state = 'slide'
            buffer = []
        elif mode_text == 'comment':
            finish_prev_state()
            state = 'comment'
        elif mode_text == 'empty':
            finish_prev_state()
            state = 'empty'
        else:
            assert False, f"Unknown mode: {mode_text}!"
        md_text = md_text[m.end():]
        continue
    return Slides(slides)

def md_to_slide_md(input_md):
    # Step2: process AST
    slides = md_to_slides(input_md)
    new_md = slides.to_slide_md_text()
    return new_md

def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} input.md output.md")
        sys.exit(1)

    input_md = Path(sys.argv[1])
    out_md = Path(sys.argv[2])
    
    assert str(input_md).endswith('.md'), "input file extension is not .md!"

    with open(input_md, 'r') as f:
        input_md_data = f.read()

    new_md = md_to_slide_md(input_md_data)

    with open(out_md, 'w') as f:
        f.write(new_md)


if __name__ == '__main__':
    main()
