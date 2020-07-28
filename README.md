# Code Reviewer

## Installation

```
git clone https://github.com/lgaspard/code-reviewer code-reviewer
```

For development, the code can be installed in editable mode with `pip install --editable code-reviewer`. This repository will thus be used as the source of the pip package, and modifications brought to this directory will be reflected directly in this package.

For usage, the package can be definitively installed with `pip install code-reviewer`, new modification brought to this directory won't be effective anymore.

## Usage

If the package has been installed with `pip`, then a system wide command `review` is available from any directory.

```
review [-h] [--port PORT] [directory]
```
