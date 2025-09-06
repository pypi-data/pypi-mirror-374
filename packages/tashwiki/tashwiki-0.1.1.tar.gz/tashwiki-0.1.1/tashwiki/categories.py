from tashwiki.utils import label_to_page_name


class Category:

    def __init__(self, categories, name):
        self.categories = categories
        self.name = name
        self.url = "{}_{}.html".format(
            self.categories.basename,
            label_to_page_name(name),
        )
        self.pages = {}

    @property
    def pages_count(self):
        return len(self.pages)

    def add_page(self, name):
        if name not in self.pages:
            self.pages[name] = label_to_page_name(name) + ".html"

    def __iter__(self):
        for name, url in self.pages.items():
            yield {"name": name, "url": url}

    def __repr__(self):
        return f"Category<{self.name}, {self.pages_count}>"

    def __lt__(self, other):
        return self.name < other.name


class Categories:

    def __init__(self, basename):
        self.basename = basename
        self.categories = []

    def get_or_create(self, name) -> Category:
        for cat in self.categories:
            if cat.name == name:
                return cat
        cat = Category(self, name)
        self.categories.append(cat)
        return cat

    def __iter__(self):
        for category in sorted(self.categories):
            yield category

    def __repr__(self):
        return f"Categories<{self.categories}>"

