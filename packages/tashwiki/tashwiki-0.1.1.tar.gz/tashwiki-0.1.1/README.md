# TashWiki

TashWiki is a wiki-like static site generator. It can be used to make your own
digital garden or simple personal wiki.

## Features

- Converts your Markdown notes into static HTML pages
- Wiki-style links between pages
- Simple and lightweight
- Easy to deploy

## Installation

```bash
pip install git+https://github.com/b00bl1k/tashwiki.git
```

## Usage

```bash
tashwiki build
```

This will take your source files from ./content and generate a static site
into ./output.

## Example

Here is a minimal note:

```markdown
# Welcome to TashWiki

This is my digital garden.

See also [[Another note]].
```

## Roadmap

- [x] Categories
- [ ] Themes
- [ ] Search

## Status

TashWiki is still in early development. Expect breaking changes.

## License

MIT

## Credits

- [[Rock icons created by Freepik - Flaticon]](https://www.flaticon.com/free-icons/rock)
