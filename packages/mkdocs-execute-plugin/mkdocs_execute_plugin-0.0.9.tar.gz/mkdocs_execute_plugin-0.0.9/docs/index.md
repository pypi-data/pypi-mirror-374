# MkDocs Execute Plugin

**MkDocs Execute Plugin** is an extension for [MkDocs](https://www.mkdocs.org/) that allows you to execute code blocks and Jupyter notebooks as part of your documentation build. It automatically runs embedded code, captures the output, and inserts the results into your documentation pages. This is ideal for scientific, technical, and educational projects that want to keep code, output, and narrative in sync.

## Features

- Execute Python code blocks, scripts, and Jupyter notebooks during documentation build
- Embed code output, figures, and errors directly in your docs
- Supports [Jupytext](https://jupytext.readthedocs.io/) formats.
- Integrates with [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) and other MkDocs themes
- Fine-grained control over execution, caching, and error handling

## Quickstart

1. Install the plugin:

   ```sh
   pip install mkdocs-execute-plugin
   ```

2. Enable it in your `mkdocs.yml`:

   ```yaml
   plugins:
     - execute
   ```

3. Add Python code blocks or Jupyter notebooks to your docs. On build, code will be executed and output embedded.

---

## Plugin Configuration & Usage

Enable the plugin by adding `execute` to the `plugins` section of your `mkdocs.yml`:

```yaml
plugins:
  - search
  - execute:
      include:
        - "*.py"
        - "*.ipynb"
        - "*.md"
      exclude: []
      execute_without_tag:
        - "*.py"
        - "*.ipynb"
      markdown_template: "markdown/index.md.j2"
      tags:
        hide_cell: "hide-cell"
        hide_input: "hide-input"
        hide_output: "hide-output"
        execute: "execute"
```

### Configuration Options

- **include**: List of glob patterns for files to execute. Default: `["*.py", "*.ipynb", "*.md"]`
- **exclude**: List of glob patterns to exclude from execution. Default: `[]`
- **execute_without_tag**: Files to execute even if the execute tag is not present. Default: `["*.py", "*.ipynb"]`
- **markdown_template**: nbconvert template for rendering executed notebooks. Default: `"markdown/index.md.j2"`
- **tags**: Sub-config for tag names used in your docs:
  - **hide_cell**: Tag to hide an entire cell. Default: `"hide-cell"`
  - **hide_input**: Tag to hide code input. Default: `"hide-input"`
  - **hide_output**: Tag to hide code output. Default: `"hide-output"`
  - **execute**: Tag to mark a file or cell for execution. Default: `"execute"`

### Advanced Usage

- **File selection**: Only files matching `include` and not matching `exclude` are considered for execution. You can use glob patterns (e.g., `docs/**/*.md`).
- **Tag-based execution**: By default, only files or cells with the `execute` tag are executed, unless the file matches `execute_without_tag`.
- **Custom tags**: You can change the tag names to fit your workflow (e.g., use `run` instead of `execute`).
- **Template customization**: The `markdown_template` option lets you specify a custom Jinja2 template for rendering executed notebooks.

### Usage Tips

- Use the `execute` tag in your markdown or notebook metadata to control execution:
  - In Markdown frontmatter or Jupytext metadata:

  ```yaml
  ---
  execute: true
  ---
  ```

  - In Jupyter notebooks, set the tag in cell metadata.

- To skip execution for a file, omit the `execute` tag or add the file to `exclude`.
- To hide code input or output, use the `hide_input` or `hide_output` tags in cell metadata.
- To hide an entire cell (e.g. if it is for initialization), use the `hide_cell` tag.
- You can customize which files are executed by editing the `include`, `exclude`, and `execute_without_tag` lists.


## Kernel Fallback Behavior

If a Jupyter notebook or Jupytext file specifies a kernel that is not available (e.g., via `kernelspec` metadata), the plugin will attempt to find a suitable fallback kernel automatically:

- The plugin searches for an installed kernel that matches the language specified in the notebook's metadata (e.g., `python`).
- If a matching kernel is found, the plugin updates the notebook's metadata to use this kernel and emits a warning in the build log indicating the fallback.
- If no suitable kernel is found, the build will fail with a `NoSuchKernel` error as before.

This behavior ensures that documentation builds are more robust to missing or renamed kernels, and helps avoid manual intervention when moving notebooks between environments.

**Example warning:**

```
WARNING -  No such kernel named nonexistent. Attempting to find a matching kernel by language...
WARNING -  Falling back to kernel 'python3' for language 'python'.
```

The output of the executed notebook will be included in your documentation as usual, even if a fallback kernel was used.

For more details, see the [project repository](https://gitlab.kwant-project.org/qt/mkdocs-execute-plugin).
