# Wrap Docstrings

Currently limited to only wrapping the argument descriptions in Google-style
docstrings.

```bash
# Install the tool globally.
git clone https://github.com/btjanaka/wrap-docstrings
uv tool install .

# This command should now work:
wrap-docstrings --help

# To format a file (must have .py extension):
wrap-docstrings file.py

# To format a directory:
wrap-docstrings DIRECTORY

# To read from stdin and write to stdout:
wrap-docstrings -

# To change width and indentation (the default values are shown below):
wrap-docstrings file.py --width 88 --indent 4
```

## Example

This text:

```python
def f(x, y):
    """Does stuff.

    Args:
        x: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure do
        y: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
            ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
            aliquip ex ea commodo consequat. Duis aute irure do

    Returns:
        Returns are not formatted (for now, at least).
    """
    return x
```

Becomes:

```python
def f(x, y):
    """Does stuff.

    Args:
        x: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat. Duis aute irure do
        y: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat. Duis aute irure do

    Returns:
        Returns are not formatted (for now, at least).
    """
    return x
```

## Integration with Neoformat

If you are using [Neoformat](https://github.com/sbdchd/neoformat) in vim, you
can configure this program as a formatter with:

```vim
let g:neoformat_python_wrap_docstrings = {
      \ 'exe': 'wrap-docstrings',
      \ 'args': ['-'],
      \ 'stdin': 1,
      \ }
let g:neoformat_enabled_python = ['wrap_docstrings'] " Or append wrap_docstrings to your current list of formatters.
```

## Suppression

To skip a file, add this comment somewhere in the file:

```python
# wrap-docstrings: disable
```
