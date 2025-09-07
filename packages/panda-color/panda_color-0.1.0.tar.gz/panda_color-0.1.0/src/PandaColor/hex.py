from .color import BaseColor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rgb import RGB

class Hex(BaseColor):
    def __init__(self, hex_string: str):
        self.hex_string = hex_string

    @classmethod
    def from_rgb(cls, rgb: RGB) -> str:
        """Convert RGB instance to hexadecimal string."""
        return f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}"