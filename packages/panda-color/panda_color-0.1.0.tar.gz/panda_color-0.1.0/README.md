# PandaColor
A lightweight and extensible Python color library.

PandaColor provides a unified interface for working with colors in multiple formats (RGB, Hex, HSV, HSL, etc.).  
It supports GLSL-style swizzling, conversions between color spaces, and convenient utilities for manipulation such as lighten, darken, invert, grayscale, and saturation adjustments.

---

## Features
- RGB support with:
  - Initialization from ints, strings, or iterables
  - GLSL-style swizzling (`color.rgb`, `color.rg`, `color.gbr`, etc.)
- Conversions between:
  - RGB ↔ Hex
  - RGB ↔ HSV
  - RGB ↔ HSL
- Manipulation methods:
  - `lighten`, `darken`, `invert`, `grayscale`
  - `saturate`, `desaturate`, `adjust_hue`
- Utilities:
  - `to_tuple()`, `to_list()`, `to_dict()`
  - CSS output (`css_rgb()`, `css_rgba()`)
  - Normalized floats `[0.0, 1.0]`

---

## Installation

Install from PyPI:

```bash
pip install pandacolor
```

Or install from source:

```bash
git clone https://github.com/ColinThePanda/pandacolor.git
cd pandacolor
pip install .
```

---

## Usage

```python
from pandacolor import RGB

# Initialize with ints
c1 = RGB(255, 128, 0)

# Initialize from iterable
c2 = RGB([0, 255, 128])

# Initialize from string
c3 = RGB("64, 128, 255")

# Swizzling
print(c1.r)      # 255
print(c1.g)      # 128
print(c1.rgb)    # (255, 128, 0)
print(c1.rg)     # (255, 128)

# Convert to Hex
print(c1.to_hex())  # Hex(#ff8000)

# Manipulation
lighter = c1.lighten(0.3)
darker = c1.darken(0.5)
inverted = c1.invert()

# CSS format
print(c1.css_rgb())       # rgb(255, 128, 0)
print(c1.css_rgba(0.5))   # rgba(255, 128, 0, 0.5)
```

---

---

## Roadmap
- Hex, HSV, HSL support
- Auto generated color palletes
- Added support for use with opengl and shaders

---

## License
MIT © 2025 Colin Politi
See [LICENSE](LICENSE) for details.