"""Custom builders."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from docutils import nodes
from sphinx import addnodes
from sphinx._cli.util.colour import darkgreen
from sphinx.builders import Builder
from sphinx.errors import SphinxError
from sphinx.locale import _
from sphinx.util.fileutil import copy_asset, copy_asset_file
from sphinx.util.nodes import inline_all_toctrees

from . import theming, writer

if TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

    from .config import DocumentSettings


class TypstBuilder(Builder):
    """Custom builder to generate Typst source from doctree."""

    name = "typst"
    format = "typst"
    default_translator_class = writer.TypstTranslator

    def __init__(self, app: Sphinx, env: BuildEnvironment) -> None:  # noqa: D107
        super().__init__(app, env)
        self._static_dir = Path(self.outdir / "_static")
        self._images_dir = Path(self.outdir / "_images")

    def init(self):  # noqa: D102
        super().init()
        self._themes: dict[str, theming.Theme] = {}

    def get_outdated_docs(self):  # noqa: D102
        return "all targets"

    def prepare_writing(self, docnames: set[str]) -> None:  # noqa: D102
        # Preload themes to copy assets before write_documents.
        def _load_theme(name: str) -> theming.Theme | None:
            if name in self._themes:
                return

            theme = theming.load_theme(name)
            theme.init(self)
            self._themes[name] = theme
            parent = theme.get_parent_theme()
            if parent:
                _load_theme(parent)

        for document_settings in self.config.typst_documents:
            _load_theme(document_settings["theme"])

    def write_documents(self, docnames):  # noqa: D102
        for document_settings in self.config.typst_documents:
            self.write_doc(document_settings)

    def write_doc(self, document_settings: DocumentSettings):  # noqa: D102
        docname = document_settings["entrypoint"]
        theme = self._themes[document_settings["theme"]]
        doctree = self.assemble_doctree(docname, document_settings["toctree_only"])
        visitor: writer.TypstTranslator = self.create_translator(doctree, self)  # type: ignore[assignment]
        doctree.walkabout(visitor)
        today_fmt = self.config.today_fmt or _("%b %d, %Y")
        context = theming.ThemeContext(
            title=document_settings["title"],
            config=self.config,
            date=date.today().strftime(today_fmt),
            body=visitor.dom.to_text(),
        )
        out = Path(self.app.outdir) / f"{document_settings['filename']}.typ"
        theme.write_doc(out, context)

    def assemble_doctree(self, docname: str, toctree_only: bool) -> nodes.document:
        """Find toctree and merge children doctree into parent doctree.

        This method is to generate single Typst document.

        .. todo::

           We must see how does inline_all_toctrees work.
        """
        root = self.env.get_doctree(docname)
        if toctree_only:
            root_section = nodes.section()
            for toctree in root.findall(addnodes.toctree):
                root_section += toctree
            root = root.copy()
            root += root_section
        tree = inline_all_toctrees(self, {docname}, docname, root, darkgreen, [docname])
        writer.transport_footnotes(tree)
        return tree

    def get_target_uri(self, docname, typ=None):  # noqa: D102
        # TODO: Implement it!
        return ""

    def copy_assets(self):  # noqa: D102
        # Copying all theme assets.
        def _copy_theme_assets():
            base_dir = self.app.outdir / "_themes"
            for name, theme in self._themes.items():
                assets_outdir = base_dir / name
                assets_srcdir = theme.get_theme_dir() / "assets"
                copy_asset(
                    assets_srcdir,
                    assets_outdir,
                )

        def _copy_static_assets():
            for entry in self.config.typst_static_path:
                copy_asset(
                    entry,
                    self._static_dir,
                )

        _copy_theme_assets()
        _copy_static_assets()

    def finish(self):  # noqa: D102
        def _copy_images():
            for src, dest in self.images.items():
                dest.parent.mkdir(parents=True, exist_ok=True)
                copy_asset_file(src, dest)

        _copy_images()


class TypstPDFBuilder(TypstBuilder):
    """PDF creation builder from doctree.

    This is similar to the relationship between
    the latexpdf builder and the latex builder.
    """

    name = "typstpdf"
    format = "typst"

    def init(self) -> None:
        """Check that python env has typst package."""
        try:
            import typst  # noqa - Only try importing
        except ImportError:
            raise SphinxError("Require 'typst' to run 'typstpdf' builder.")
        super().init()

    def finish(self):  # noqa: D102
        import typst

        super().finish()
        for document_settings in self.config.typst_documents:
            src = Path(self.app.outdir) / f"{document_settings['filename']}.typ"
            out = Path(self.app.outdir) / f"{document_settings['filename']}.pdf"
            typst.compile(src, output=out)
