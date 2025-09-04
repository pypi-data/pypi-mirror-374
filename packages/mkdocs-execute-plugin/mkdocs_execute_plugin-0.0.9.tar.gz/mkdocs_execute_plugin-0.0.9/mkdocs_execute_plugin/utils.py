from pathlib import Path

from jupytext import jupytext
from markdown import Markdown

truthy_values = ["true", "yes", "1", "on"]
falsy_values = ["false", "no", "0", "off"]
bool_values = truthy_values + falsy_values


def is_truthy(value):
    if isinstance(value, list):
        value = value.pop()
    return value in truthy_values


def is_markdown_file(file_path):
    return file_path.endswith(".md")


def extract_tag_jupytext(file_path, tag):
    with Path(file_path).open("r") as notebook_file:
        notebook = jupytext.read(notebook_file)

    has_tag = False
    tag_value = None
    try:
        tag_value = notebook.metadata[tag]
        has_tag = True
    except (AttributeError, KeyError):
        pass

    return has_tag, tag_value


def extract_tag_markdown(file_path, tag):
    md = Markdown(extensions=["meta"])
    md.convert(Path(file_path).read_text())
    if tag not in md.Meta:
        return False, None

    return True, md.Meta[tag]
