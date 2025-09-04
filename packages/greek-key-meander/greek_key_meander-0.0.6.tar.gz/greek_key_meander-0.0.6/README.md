# Greek Key Meander Generator

[![PyPI version](https://badge.fury.io/py/greek-key-meander.svg)](https://badge.fury.io/py/greek-key-meander)

This Python script generates Greek key meander patterns as SVG and PNG images.

> **Warning**
> This package has been deprecated and is no longer maintained.
> Please use the new package [greek_meander](https://github.com/bingqiao/greek_meander) instead.

## Demo

![Meander](meander.png)

## Description

The script uses the `drawsvg` library to create the pattern and `cairosvg` to convert it to a PNG image. The pattern's dimensions, colors, and other properties can be customized through command-line arguments.

## Installation

You can install the package from PyPI:

```bash
pip install greek_key_meander
```

This will also install the required dependencies: `drawsvg` and `cairosvg`.

## Usage

You can run the script from the command line and specify various arguments to customize the output.

```bash
python -m meander [options]
```

### Options

| Argument | Type | Default | Description |
|---|---|---|---|
| `--stroke-width` | float | 6.0 | Line thickness in pixels. |
| `--stroke-color` | str | '#AB8E0E' | Line color (name, hex, or RGB). |
| `--stroke-opacity`| float | 0.7 | Line transparency (0.0 to 1.0). |
| `--size` | int | 25 | Size of the pattern unit. |
| `--width` | int | 16 | Number of patterns horizontally. |
| `--height` | int | 9 | Number of patterns vertically. |
| `--file` | str | 'meander' | Output filename for SVG and PNG. |

### Example

To generate a pattern with a red color and a different size:

```bash
python -m meander --stroke-color red --width 10 --height 5
```

Or just the following if the module is installed:
```bash
meander --width 24 --height 13 --size 10 --stroke-color "#AB8E0E" --stroke-opacity 0.7
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
