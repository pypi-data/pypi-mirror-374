
import logging
from pathlib import Path
from shutil import copytree
from importlib import resources

from markdown import Markdown
from jinja2 import Environment, PackageLoader, TemplateNotFound
from termcolor import cprint

from tashwiki.categories import Categories, Category
from tashwiki.config import Config
from tashwiki.utils import page_name_to_label, label_to_page_name
from tashwiki.wikilinks import WikiLinkExtension

logger = logging.getLogger()


class Builder:
    DEFAULT_PAGE_TEMPLATE = "page.html"
    CATEGORIES_PAGE_TEMPLATE = "categories.html"
    CATEGORY_TEMPLATE = "category.html"

    def __init__(self, config: Config):
        self.conf = config
        self.source_dir = Path(config.site_source_dir)
        self.output_dir = Path(config.site_output_dir)
        self.glob_context = self._prepare_context()
        self.env = Environment(
            loader=PackageLoader("tashwiki"),
        )
        self.categories = Categories(config.site_category_page)
        self.md = Markdown(extensions=[
            "meta",
            "fenced_code",
            WikiLinkExtension(
                base_url=config.site_baseurl,
                end_url=".html",
                html_class=self._build_link_class,
            )
        ])

    def _prepare_context(self) -> dict:
        return {
            "site_author": self.conf.site_author,
            "site_name": self.conf.site_name,
            "baseurl": self.conf.site_baseurl,
            "language": self.conf.site_language,
            "main_page": self.conf.site_main_page,
            "categories_page": self.conf.site_categories_page,
            "categories_url": label_to_page_name(self.conf.site_categories_page) + ".html",
            "category_page": self.conf.site_categories_page,
            "category_url": label_to_page_name(self.conf.site_categories_page) + ".html",
        }

    def _build_link_class(self, page: str):
        """Return css class for link."""

        page_name = label_to_page_name(page)
        page_path = (self.source_dir / page_name).with_suffix(".md")
        if not page_path.exists():
            cprint(f"Missing page '{page_name}'", color="red")
            return "notfound"
        return ""

    def _render_html_page(self, out_path: Path, template: str, context: dict):
        """Render page using Jinja template engine and write to output file."""

        template = self.env.get_template(template)
        html = template.render(context)
        out_path.write_text(html, encoding="utf-8")

    def _validate_meta(self, meta: dict) -> dict:
        """Validate meta information from Markdown document."""

        for key, value in meta.items():
            if key in ("title", "author"):
                meta[key] = value[0]
            elif key == "template":
                tpl = value[0]
                try:
                    env.get_template(tpl)
                    meta[key] = tpl
                except TemplateNotFound:
                    raise ValueError(f"Template '{tpl}' not found.")
            elif key == "categories":
                pass
            else:
                raise ValueError(f"Unknown meta field '{key}'.")
        return meta

    def _copy_static(self):
        with resources.as_file(resources.files("tashwiki.static")) as src_path:
            copytree(src_path, self.output_dir, dirs_exist_ok=True)

        static_dir = Path(self.conf.site_static_dir)
        if static_dir.exists():
            copytree(static_dir, self.output_dir, dirs_exist_ok=True)

    def build(self):
        """Build site to output folder."""

        print(f"Building site to folder '{self.output_dir}'...")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for md_file in self.source_dir.rglob("*.md"):
            print(f"Rendering '{md_file.stem}'...")
            self.render_page(md_file)

        for category in self.categories:
            print(f"Rendering category page '{category.name}'...")
            self.render_category_page(category)

        print("Rendering categories index page...")
        self.render_categories_index()

        print("Copying static files...")
        self._copy_static()

    def render_page(self, md_file: Path):
        """Convert Markdown document to HTML page."""

        page_content = self.md.convert(md_file.read_text(encoding="utf-8"))
        page_name = md_file.stem
        page_title = page_name_to_label(page_name)

        # prepare context for rendering
        page_context = {
            "page_content": page_content,
            "title": page_title,
        }
        page_context.update(self.glob_context)

        # document can contain some meta information
        meta = self._validate_meta(self.md.Meta)
        page_template = meta.pop("template", self.DEFAULT_PAGE_TEMPLATE)
        category_names = meta.pop("categories", [])
        page_context.update(meta)

        # extract categories from meta and update context
        page_categories = []
        for category_name in category_names:
            category = self.categories.get_or_create(category_name)
            category.add_page(page_title)
            page_categories.append(category)
        page_context.update({"categories": page_categories})

        # actual render to a file
        out_path = self.output_dir / md_file.with_suffix(".html").name
        self._render_html_page(out_path, page_template, page_context)

    def render_categories_index(self):
        categories_context = {
            "categories": list(self.categories),
            "title": self.conf.site_categories_page,
        }
        categories_context.update(self.glob_context)
        out_path = (self.output_dir / self.conf.site_categories_page).with_suffix(".html")
        self._render_html_page(out_path, self.CATEGORIES_PAGE_TEMPLATE, categories_context)

    def render_category_page(self, category: Category):
        category_context = {
            "category": category,
            "title": f"{self.conf.site_category_page}: {category.name}"
        }
        category_context.update(self.glob_context)
        out_path = self.output_dir / category.url
        self._render_html_page(out_path, self.CATEGORY_TEMPLATE, category_context)
