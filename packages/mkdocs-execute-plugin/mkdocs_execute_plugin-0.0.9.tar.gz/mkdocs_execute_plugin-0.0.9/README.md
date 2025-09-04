# MkDocs Execute Plugin

Plugin for MkDocs that executes documentation files using jupytext and embeds the output in your documentation.

## Installation

Start by install the plugin using pip:

```bash
pip install mkdocs-execute-plugin
```

## Basic usage

### Configuring mkdocs

After installing it, you can enable the plugin by adding it to the `plugin` section of your `mkdocs.yml`:

```yml
plugins:
  - execute
```

### Adding executable files

By default, this plugin will execute all code blocks inside markdown files if the file has the `execute` tag. An example markdown file can be found below.

````yml
---
execute: true
---

```python
print('Hello world!')
```
````

On top of that, the plugin will also execute all python (`.py`) files by default.

```python
print('Hello world!')
```

### Hiding cell input or output

It is possible to hide the input or output of a cell by applying the `hide-input` and `hide-output` tags respectively. It is also possible to hide a cell completely using the `hide-cell`
 tag.

````yml
```python tags=["hide-input"]
print('Hidden input')
```

```python tags=["hide-output"]
print('Hidden output')
```

```python tags=["hide-cell"]
print('Completely hidden')
```
````

## Configuration

All configuration options can be found below. The given values are the defaults.

```yml
# Default configuration
plugins:
  - execute:
      # Specify which files to include for execution. Should be a list of .gitignore style glob patterns.
      # Note that only files with the execute tag set to true will be executed. To override, see `execute_without_tag`.
      include:
        - '*.py'
        - '*.md'
      # Specify which glob patterns to exclude for execution. Same format as `include`.
      exclude: []
      # Specify which files should still be executed if the execute tag is missing. Same format as `include`.
      # If the execute is set to false for a file matching this pattern, it will NOT be executed.
      execute_without_tag:
        - '*.py'
      # Markdown template used to render the executed files.
      markdown_template: 'markdown/index.md.j2'
      # You can modify the names of all tags.
      tags:
        # Tag that marks the file as executable.
        execute: 'execute'
        # Tag that hides a cell completely, both the input and output.
        # Note that the cell will still be executed.
        hide_cell: 'hide-cell'
        # Tag that hides the cell input (code).
        hide_input: 'hide-input'
        # Tag that hides the cell output.
        hide_output: 'hide-output'
```

## Supported formats and languages

This plugin uses [jupytext](https://github.com/mwouts/jupytext) to execute and then convert files to markdown. This means all languages and formats supported by jupytext should work.

## Development with Pixi

This repo is configured to use [Pixi](https://pixi.sh) for fast, reproducible environments and dev tasks.

1. Install Pixi (one-time)

```sh
curl -fsSL https://pixi.sh/install.sh | sh
```

1. Install the environment (creates `.pixi/` locally)

```sh
pixi install
```

1. Common tasks

```sh
# Run tests
pixi run test

# Build and serve the docs
pixi run docs-build
pixi run docs-serve
```

You can also open a shell in the environment:

```sh
pixi shell
```

## Pre-commit hooks

This repo uses pre-commit to enforce code style and basic checks:

```sh
# Install git hooks
pixi run pre-commit install

# Run hooks on all files
pixi run pre-commit-run
```

CI will also run `pre-commit run --all-files` to keep the codebase consistent.
