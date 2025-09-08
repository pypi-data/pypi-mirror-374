[![PyPI version](https://badge.fury.io/py/readme_llm7_gen.svg)](https://badge.fury.io/py/readme_llm7_gen)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/readme_llm7_gen)](https://pepy.tech/project/readme_llm7_gen)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# readme_llm7_gen

`readme_llm7_gen` is a Python package that leverages language models to generate polished README.md files for your Python projects. It simplifies creating comprehensive documentation by analyzing your package content and supplementary metadata.

## Installation

Install via pip:

```bash
pip install readme_llm7_gen
```

## Usage

You can generate a README by providing your package's source code and optional metadata. Here's a quick example:

```python
from readme_llm7_gen import generate_readme_from_llm

package_code = '''
def add(a, b):
    return a + b
'''

readme_content = generate_readme_from_llm(
    package_text=package_code,
    author_name="Eugene Evstafev",
    author_email="hi@eugene.plus",
    repo_link="https://github.com/chigwell/readme_llm7_gen",
    verbose=True
)

print(readme_content)
```

This will produce a detailed README.md content based on your package code and metadata, wrapped appropriately.

## Features

- Automates the creation of README.md files using LLMs.
- Supports inclusion of author and repository info.
- Customizable and easy to integrate into your workflow.
- Capable of processing raw package source code.

## Author

Eugene Evstafev <hi@eugene.plus>

## Repository

[https://github.com/chigwell/readme_llm7_gen](https://github.com/chigwell/readme_llm7_gen)
