import os
import uuid
from logging import getLogger
from pathlib import Path
from time import perf_counter

import jupytext
import mkdocs
import nbconvert
from jupyter_client.kernelspec import KernelSpecManager, NoSuchKernel
from mkdocs.config import config_options as c
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from nbconvert.preprocessors import ExtractOutputPreprocessor
from traitlets.config import Config

from . import utils

logger = getLogger("mkdocs.plugins.execute")

# Based on https://gitlab.kwant-project.org/solidstate/lectures/-/blob/b424707f5aeba31f276bfd0495f82a852750a2d2/execute.py


class AlreadySavedFile(File):
    def copy_file(self, dirty=False):
        pass


class ExecutableFile(File):
    """A file that should be executed. This is a wrapper around the mkdocs File"""

    # Based on https://github.com/danielfrg/mkdocs-jupyter/blob/93bb183544dc024b4de2a0c9341328ae7317e3db/src/mkdocs_jupyter/plugin.py#L15

    def __init__(self, file, use_directory_urls, site_dir, **kwargs):
        self.file = file
        self.dest_path = self._get_dest_path(use_directory_urls)
        self.abs_dest_path = str((Path(site_dir) / self.dest_path).resolve())
        self.url = self._get_url(use_directory_urls)

    def __getattr__(self, item):
        return self.file.__getattribute__(item)

    def is_documentation_page(self) -> bool:
        return True


class TagConfig(mkdocs.config.base.Config):
    hide_cell = c.Type(str, default="hide-cell")
    hide_input = c.Type(str, default="hide-input")
    hide_output = c.Type(str, default="hide-output")
    execute = c.Type(str, default="execute")


class ExecuteConfig(mkdocs.config.base.Config):
    include = c.ListOfItems(c.PathSpec(), default=["*.py", "*.ipynb", "*.md"])
    exclude = c.ListOfItems(c.PathSpec(), default=[])
    execute_without_tag = c.ListOfItems(c.PathSpec(), default=["*.py", "*.ipynb"])
    markdown_template = c.Type(str, default="markdown/index.md.j2")
    tags = c.SubConfig(TagConfig)


class ExecutePlugin(BasePlugin[ExecuteConfig]):
    exporter: nbconvert.TemplateExporter

    def __init__(self):
        self.output_map = {}
        # TODO: Is this the right place to configure this?
        os.environ["PLOTLY_RENDERER"] = "plotly_mimetype"

    def on_config(self, config):
        output_extractor = ExtractOutputPreprocessor()
        output_extractor.extract_output_types = (
            output_extractor.extract_output_types | {"application/vnd.plotly.v1+json"}
        )

        tag_remove_processor = nbconvert.preprocessors.TagRemovePreprocessor()
        tag_remove_processor.remove_cell_tags = {
            self.config.tags.hide_cell,
        }
        tag_remove_processor.remove_all_outputs_tags = {
            self.config.tags.hide_output,
        }
        tag_remove_processor.remove_input_tags = {
            self.config.tags.hide_input,
        }

        self.exporter = nbconvert.TemplateExporter(
            config=Config(
                dict(
                    TemplateExporter=dict(
                        preprocessors=[
                            nbconvert.preprocessors.ExecutePreprocessor,
                            tag_remove_processor,
                            output_extractor,
                        ],
                        exclude_input=False,
                        template_file=self.config.markdown_template,
                    ),
                    NbConvertBase=dict(
                        display_data_priority=[
                            "application/vnd.plotly.v1+json",
                            "text/html",
                            "text/markdown",
                            "image/svg+xml",
                            "text/latex",
                            "image/png",
                            "image/jpeg",
                            "text/plain",
                        ]
                    ),
                )
            )
        )

    def on_files(self, files, config):
        return Files(
            [
                ExecutableFile(file, **config) if self._should_execute(file) else file
                for file in files
            ]
        )

    def on_page_read_source(self, page, config, **kwargs):
        if not isinstance(page.file, ExecutableFile):
            return

        abs_src_path = Path(page.file.abs_src_path)
        notebook = jupytext.read(abs_src_path)

        src_dir = Path(page.file.src_path).parent
        build_directory = Path(config.site_dir) / src_dir
        relative_path = abs_src_path.relative_to(config.docs_dir)
        logger.info(f"Executing {relative_path}")
        start = perf_counter()
        try:
            output, resources = self.exporter.from_notebook_node(
                notebook,
                resources={
                    "unique_key": abs_src_path.name,
                    # Compute the relative URL
                    "output_files_dir": "_execute_outputs",
                    "metadata": {"path": abs_src_path.parent},
                },
            )
        except NoSuchKernel as e:
            # Try to find a matching kernel by language
            logger.warning(
                f"No such kernel named {e.args[0]}. Attempting to find a matching kernel by language..."
            )
            ksm = KernelSpecManager()
            nb_kernel = notebook.metadata.get("kernelspec", {})
            nb_language = nb_kernel.get("language", "python")
            found = None
            for name in ksm.find_kernel_specs():
                spec = ksm.get_kernel_spec(name)
                if spec.language.lower() == nb_language.lower():
                    found = (name, spec)
                    break
            if found:
                logger.warning(
                    f"Falling back to kernel '{found[0]}' for language '{nb_language}'."
                )
                # Update notebook metadata
                notebook.metadata["kernelspec"] = {
                    "name": found[0],
                    "display_name": found[1].display_name,
                    "language": found[1].language,
                }
                # Recreate exporter with correct kernel_name in config
                from traitlets.config import Config as TraitletsConfig

                fallback_config = TraitletsConfig(
                    {
                        "ExecutePreprocessor": {"kernel_name": found[0]},
                        "TemplateExporter": self.exporter.config.get(
                            "TemplateExporter", {}
                        ),
                        "NbConvertBase": self.exporter.config.get("NbConvertBase", {}),
                    }
                )
                fallback_exporter = nbconvert.TemplateExporter(config=fallback_config)
                fallback_exporter.template_file = self.exporter.template_file
                output, resources = fallback_exporter.from_notebook_node(
                    notebook,
                    resources={
                        "unique_key": abs_src_path.name,
                        "output_files_dir": "_execute_outputs",
                        "metadata": {"path": abs_src_path.parent},
                    },
                )
            else:
                logger.error(f"No kernel found for language '{nb_language}'.")
                raise
        end = perf_counter()
        logger.info(f"Executed {relative_path} in {end - start:.2f} seconds.")
        temporary_file_name = f"{str(uuid.uuid4())}.md"
        nbconvert.writers.FilesWriter(build_directory=str(build_directory)).write(
            output, resources, temporary_file_name
        )
        temporary_file_path = build_directory / temporary_file_name
        source = temporary_file_path.read_text()
        temporary_file_path.unlink()
        self.output_map[str(abs_src_path)] = list(
            src_dir / output for output in resources["outputs"].keys()
        )
        return source

    def on_page_markdown(self, markdown, page, config, files):
        src_path = page.file.abs_src_path
        if src_path not in self.output_map:
            return

        for file in self.output_map.pop(src_path):
            files.append(
                AlreadySavedFile(
                    str(file),
                    config.docs_dir,
                    config.site_dir,
                    config.use_directory_urls,
                )
            )

    def _should_execute(self, file: File):
        src_path = Path(file.src_path)

        def matches_any(globs):
            for glob in globs:
                if glob.match_file(src_path):
                    return True

        if not matches_any(self.config.include):
            return False

        if matches_any(self.config.exclude):
            return False

        if utils.is_markdown_file(file.src_path):
            # Jupytext does not preserve markdown metadata, so we extract from markdown directly
            extract_tag = utils.extract_tag_markdown
        else:
            extract_tag = utils.extract_tag_jupytext

        has_execute_tag, execute_tag_value = extract_tag(
            file.abs_src_path, self.config.tags.execute
        )

        if not has_execute_tag and matches_any(self.config.execute_without_tag):
            return True

        return has_execute_tag and utils.is_truthy(execute_tag_value)
