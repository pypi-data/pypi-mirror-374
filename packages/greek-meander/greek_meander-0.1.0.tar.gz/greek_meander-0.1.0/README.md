# Greek Key Meander Generator

[![PyPI version](https://badge.fury.io/py/greek-meander.svg)](https://badge.fury.io/py/greek-meander)

This Python script generates Greek key meander patterns as SVG and PNG images.

## Examples

### Rectangle

![Meander Rectangle](https://raw.githubusercontent.com/bingqiao/greek_meander/refs/heads/master/images/meander_rectangle.png)

### Circle

![Meander Circle](https://raw.githubusercontent.com/bingqiao/greek_meander/refs/heads/master/images/meander_circle.png)

## Description

The script uses the `drawsvg` library to create the pattern and `cairosvg` to convert it to a PNG image. The pattern's dimensions, colors, and other properties can be customized through command-line arguments.

## Installation

You can install the package from PyPI:

```bash
pip install greek_meander
```

This will also install the required dependencies: `drawsvg` and `cairosvg`.

Or you can install via `pip` the two packages above then run the script `meander.py` directly.

## Usage

The script can be run from the command line with different subcommands to generate various types of meander patterns.

### General Options

These options apply to all pattern types:

| Argument | Type | Default | Description |
|---|---|---|---|
| `--stroke-width` | float | 2.0 | Line thickness in pixels. |
| `--stroke-color` | str | '#AB8E0E' | Line color (name, hex, or RGB). |
| `--stroke-opacity`| float | 0.7 | Line transparency (0.0 to 1.0). |
| `--border-margin` | int | 1 | The margin of borders. |
| `--file` | str | 'meander' | Output filename for SVG and PNG. |

N.B. you need to have general options before `rect` or `circle` subcommand, followed by subcommand specific options.

### Rectangle Pattern

To generate a rectangular meander pattern, use the `rect` subcommand.

```bash
meander rect [options]
```

#### Rectangle Options

| Argument | Type | Default | Description |
|---|---|---|---|
| `--size` | int | 10 | Size of the pattern unit. |
| `--width` | int | 16 | Number of patterns horizontally. |
| `--height` | int | 9 | Number of patterns vertically. |

#### Rectangle Example

To run the python script directly

```bash
python meander.py --stroke-color "#AB8E0E" --stroke-opacity 0.7 rect --width 24 --height 13 --size 10
```

Or if you installed `greak_meander`

```bash
meander --stroke-color "#AB8E0E" --stroke-opacity 0.7 rect --width 24 --height 13 --size 10
```

### Circle Pattern

To generate a circular meander pattern, use the `circle` subcommand.

```bash
meander circle [options]
```

#### Circle Options

| Argument | Type | Default | Description |
|---|---|---|---|
| `--pattern-count` | int | 30 | Number of patterns in the circle. |
| `--radius` | int | 300 | The radius of the circle. |

#### Circle Example
To run the python script directly

```bash
python meander.py --stroke-color green --file images/meander_circle circle
```

Or if you installed `greak_meander`

```bash
meander --stroke-color green --file images/meander_circle circle
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.