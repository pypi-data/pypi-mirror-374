import subprocess
import json
from pathlib import Path
from functools import cache
from copy import copy
import os
import sys

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
project_dir = os.path.dirname(script_dir)

@cache
def _empty_ast_val() -> dict:
    return md_to_ast('')

def empty_ast() -> dict:
    return copy(_empty_ast_val())

def wrap_ast(ast):
    val = empty_ast()
    assert type(ast) is list
    val['blocks'] = ast
    return val

def md_to_ast(input_md: str) -> dict:
    # Convert input markdown to pandoc JSON AST
    result = subprocess.run([
        "pandoc", "-f", "markdown", "-t", "json"
    ], input=input_md , capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def write_pandoc_json(doc: dict, output_path: Path):
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)


def ast_to_markdown(json_path: Path, md_path: Path):
    subprocess.run([
        "pandoc", str(json_path), "-f", "json", "-t", "markdown"
    ], check=True)

def ast_to_markdown(val) -> str:
    """
    Convert a Pandoc JSON AST (as a JSON string) directly to Markdown string using subprocess pipes.

    Args:
        json_str: The Pandoc AST in JSON format as a string.
    Returns:
        The converted Markdown as a string.
    """
    if type(val) is dict or type(val) is list:
        if type(val) is list:
            val = wrap_ast(val)
        val = json.dumps(val, indent=2, ensure_ascii=False)
    assert type(val) is str, 'Wrong type!'
    try:
        result = subprocess.run(
            ["pandoc", "-f", "json", "-t", "markdown"],
            input=val,
            text=True,
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error: convert ast to markdown failed!")
        print(e.stderr)
        print(val)
        raise e
    return result.stdout

def text_to_speech(text, output_path, lang=None, speed=1.0):
    from .tts.kokoro import text_to_speech
    text_to_speech(text, output_path, lang, speed)
