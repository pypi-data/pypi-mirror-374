import os
from configparser import ConfigParser, Error


class Config:

    def __init__(self, config: ConfigParser):
        self.conf = config

    @classmethod
    def from_file(cls, file: str):
        if not os.path.exists(file):
            raise ValueError("Config file not found.")
        try:
            config_parser = ConfigParser()
            config_parser.read(file)
            return cls(config_parser)
        except Error:
            raise ValueError("Config file is invalid.")

    @classmethod
    def default(cls):
        config_parser = ConfigParser()
        return cls(config_parser)

    @property
    def site_author(self):
        return self.conf.get("site", "author", fallback="")

    @property
    def site_name(self):
        return self.conf.get("site", "name", fallback="TashWiki")

    @property
    def site_language(self):
        return self.conf.get("site", "language", fallback="en")

    @property
    def site_baseurl(self):
        return self.conf.get("site", "baseurl", fallback="/")

    @property
    def site_source_dir(self):
        return self.conf.get("site", "source_dir", fallback="content")

    @property
    def site_static_dir(self):
        return self.conf.get("site", "static_dir", fallback="content/static")

    @property
    def site_output_dir(self):
        return self.conf.get("site", "output_dir", fallback="output")

    @property
    def site_main_page(self):
        return self.conf.get("site", "main_page", fallback="Main page")

    @property
    def site_categories_page(self):
        return self.conf.get("site", "categories_page", fallback="Categories")

    @property
    def site_category_page(self):
        return self.conf.get("site", "category_page", fallback="Category")
