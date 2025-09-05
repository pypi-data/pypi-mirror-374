import sys,os
from pathlib import Path
from .md2slidemd import md_to_ast, md_to_slides
from .utils import *


def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} input.md output.mkv")
        sys.exit(1)

    input_md = Path(sys.argv[1])
    tmp_folder = Path(sys.argv[1]+'.md2video')
    os.makedirs(tmp_folder, exist_ok=True)
    out_video = Path(sys.argv[2])

    assert str(input_md).endswith('.md')
    assert str(out_video).endswith('.mkv')

    with open(input_md, 'r') as f:
        input_md_data = f.read()

    slides = md_to_slides(input_md_data)
    slides.set_workdir(tmp_folder)
    slides.create_video('out.mkv')

if __name__ == '__main__':
    main()
