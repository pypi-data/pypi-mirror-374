# print_fa

`print_fa` is a Python library designed to address common issues with printing Persian (Farsi) text in various environments, especially in terminals like VS Code where right-to-left (RTL) text display, character shaping, and proper alignment can be problematic.

## Features

- **Correct Persian Text Display**: Ensures proper rendering of Persian characters, handling ligatures and character joining.
- **Right-to-Left (RTL) Support**: Automatically adjusts text direction for correct RTL display.
- **Colored Output**: Easily print Persian text in various colors.
- **Styling Options**: Apply bold and underline styles to your Persian text.
- **User-Friendly**: Simple and intuitive API for easy integration into your Python projects.
- **Optimized for Performance**: Designed to be efficient for both small scripts and large-scale applications.

## Installation

YouYou can install `print_fa` using pip:

```bash
pip install print-fa
```

## Usage

Here's how to use `print_fa` in your Python code:

```python
from print_fa import print_fa

# Basic usage
print_fa("سلام دنیا")

# With color
print_fa("متن قرمز", color="red")

# With bold style
print_fa("متن پررنگ", bold=True)

# With underline style
print_fa("متن زیرخط", underline=True)

# With multiple styles
print_fa("متن آبی و پررنگ", color="blue", bold=True)

# Persian text mixed with English
print_fa("این یک متن فارسی است با کلمات English در آن.")
```

## Available Colors

You can use the following color names (case-insensitive):

- `black`
- `red`
- `green`
- `yellow`
- `blue`
- `magenta`
- `cyan`
- `white`

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests on the GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

httex


