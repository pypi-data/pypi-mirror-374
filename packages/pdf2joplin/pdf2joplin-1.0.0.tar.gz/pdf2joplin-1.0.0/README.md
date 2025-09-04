<a id="readme-top"></a>

<br />

<div align="center">

[![Python][python-shield]][python-url]
[![Linux][linux-shield]][linux-url]
[![MacOS][macos-shield]][macos-url]
[![Stars][stars-shield]][stars-url]
[![Contributors][contributors-shield]][contributors-url]
[![Lint][lint-shield]][lint-url]
[![Issues][issues-shield]][issues-url]

  <p align="center">
    Convert your PDF documents to Markdown notes with KaTeX support with the help of OpenAI.
    <br />
    <br />
    <a href="https://github.com/xcalts/pdf2joplin/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/xcalts/pdf2joplin/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
    ·
    <a href="https://pypi.org/project/pdf2joplin/">PyPI</a>
  </p>

</div>

## Features

- Takes as INPUT a pdf and transforms it into Markdown with KaTeX using OpenAI.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Installation

You can install `pdf2joplin` using `pip`.

```
pip install pdf2joplin
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

If you are using Mac, then you need to install [poppler](https://poppler.freedesktop.org/).

```txt
brew install poppler
```

After installing it, you can run it like this:

```txt
> pdf2joplin --help

Usage: pdf2joplin [OPTIONS]

  Convert your PDF documents to Markdown notes with KaTeX support with the help of OpenAI.

Options:
  --version          Show the version and exit.
  --pdf TEXT         The filepath of the PDF that you wish to convert.  [required]
  --output TEXT      The filepath of the final markdown file.  [required]
  --openai-key TEXT  The OpenAI key used to perform the prompt queries.  [required]
  --skip INTEGER     Number of pages to skip.
  --help             Show this message and exit.
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Developing

In order to start developing you will need to to follow the instructions below.

```txt
> pyenv install 3.12.6
> pyenv global 3.12.6
> python3 -m venv .venv
> source .venv/bin/activate
> (.venv) pip install ruff pre-commit
> (.venv) pip install -e .
> (.venv) pdf2joplin --version
> (.venv) ruff check --fix
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Dependencies

- [click](https://github.com/pallets/click)
- [pdf2image](https://github.com/Belval/pdf2image)
- [openai-python](https://github.com/openai/openai-python)
- [pydantic](https://github.com/openai/openai-python)
- [tqdm](https://github.com/tqdm)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request.
You can also simply open an issue with the tag "enhancement".

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/xcalts/pdf2joplin.svg?style=flat
[contributors-url]: https://github.com/xcalts/pdf2joplin/graphs/contributors
[lint-shield]: https://img.shields.io/github/actions/workflow/status/xcalts/pdf2joplin/ruff.yml?style=flat&label=ruff-lint
[lint-url]: https://github.com/xcalts/pdf2joplin/actions/workflows/lint.yml
[stars-shield]: https://img.shields.io/github/stars/xcalts/pdf2joplin.svg?style=flat
[stars-url]: https://github.com/xcalts/pdf2joplin/stargazers
[issues-shield]: https://img.shields.io/github/issues/xcalts/pdf2joplin.svg?style=flat
[issues-url]: https://github.com/xcalts/pdf2joplin/issues
[license-shield]: https://img.shields.io/github/license/xcalts/pdf2joplin.svg?style=flat
[license-url]: https://github.com/xcalts/pdf2joplin/blob/master/LICENSE
[python-shield]: https://img.shields.io/badge/Python-black?logo=python
[python-url]: https://www.python.org/
[linux-shield]: https://img.shields.io/badge/Linux-black?logo=linux
[linux-url]: https://www.linux.org/
[macos-shield]: https://img.shields.io/badge/Darwin-black?logo=macos
[macos-url]: https://www.apple.com/
