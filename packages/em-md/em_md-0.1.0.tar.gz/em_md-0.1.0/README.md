# Em-Md

_tools for processing markdown files & projects with python & CLI_

## Features

- **Local Links Processor**  
  Rewrite Markdown links and embedded media paths in all markdown files in the directory specified with the `--root` option:
  - `--mode to-absolute`: convert relative links into root-absolute links (relative to your project root).
  - `--mode to-relative`: convert absolute links (that point to existing files within the project) back into relative paths.
  - Supports inline links/images, reference-style links, and HTML embeds (`<img>`, `<a>`, `<video>`, `<audio>`, `<source>`).
  - Skips code blocks and inline code to avoid accidental rewrites.
  - Flexible output: root-absolute (`/path/file.md`), `file:///` URLs, or URLs with a base (e.g. `https://example.com/...`).
  - CLI with dry-run (`--print-changes`), in-place rewrite (`--write`), and automatic backups (`--backup`).

This is just the first tool — more Markdown utilities will be added to the **Em-Md toolbox** over time.

## Quickstart

Install on local machine:

```bash
pip install em-md
```

Run the **local links** processor on your project:

```bash
em-md-change-links \
  --root . \
  --glob "**/*.md" \
  --mode to-absolute \
  --print-changes
```

Apply changes in place (with backups):

```bash
em-md-change-links \
  --root . \
  --glob "**/*.md" \
  --mode to-absolute \
  --write --backup
```

Convert absolute paths back to relative paths:

```bash
em-md-change-links \
  --root . \
  --glob "**/*.md" \
  --mode to-relative \
  --write
```

## Documentation

* [Full Documentation](docs/README.md):

  * [Usage](docs/Usage/README.md)
  * [API-Reference](docs/API-Reference/README.html)

## DevOps

To get started using this repository's code, checkout the commands built into its Makefile by running:
```sh
make help
```

## Roadmap

* Extend `local_links` with smarter path handling for cross-project references.
* Add more Markdown processing tools:

  * frontmatter manager
  * heading/link normalizer
  * link checker / validator
* Provide `em-md` as an installable CLI entrypoint (`pip install em-md`).
* Package docs with worked examples and best practices.

## Contributing

### Get Involved

- GitHub Discussions: if you want to share ideas
- GitHub Issues: if you find bugs, other issues, or would like to submit feature requests
- GitHub Merge Requests: if you think you know what you're doing, you're very welcome!

### Donations

To support me in my work on this and other projects, you can make donations with the following currencies:

- **Bitcoin:** `BC1Q45QEE6YTNGRC5TSZ42ZL3MWV8798ZEF70H2DG0`
- **Ethereum:** `0xA32C3bBC2106C986317f202B3aa8eBc3063323D4`
- [**Fiat** (via Credit or Debit Card, Apple Pay, Google Pay, Revolut Pay)](https://checkout.revolut.com/pay/4e4d24de-26cf-4e7d-9e84-ede89ec67f32)

Donations help me:
- dedicate more time to developing and maintaining open-source projects
- cover costs for IT infrastructure
- finance projects requiring additional hardware & compute

## About the Developer

This project is developed by a human one-man team, publishing under the name _Emendir_.  
I build open technologies trying to improve our world;
learning, working and sharing under the principle:

> _Freely I have received, freely I give._

Feel welcome to join in with code contributions, discussions, ideas and more!

## Open-Source in the Public Domain

I dedicate this project to the public domain.
It is open source and free to use, share, modify, and build upon without restrictions or conditions.

I make no patent or trademark claims over this project.  

Formally, you may use this project under either the: 
- [MIT No Attribution (MIT-0)](https://choosealicense.com/licenses/mit-0/) or
- [Creative Commons Zero (CC0)](https://choosealicense.com/licenses/cc0-1.0/)
licence at your choice.  


