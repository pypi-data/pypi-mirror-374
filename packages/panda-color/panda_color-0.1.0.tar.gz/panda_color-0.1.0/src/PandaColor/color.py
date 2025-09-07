from typing import Union, Iterable, Tuple
import numbers

from abc import ABC, abstractmethod
from typing import Tuple, Union, Iterator, Any, TYPE_CHECKING
import numbers
import math

if TYPE_CHECKING:
    from typing_extensions import Self
    from .rgb import RGB
    from .hex import Hex
    from .hsv import HSV

class BaseColor(ABC):
    """
    Abstract base class for all color representations.
    
    Provides common color operations, conversions, and validation.
    All color classes (RGB, Hex, HSL, HSV, etc.) should inherit from this.
    """
    
    # Color space bounds
    RGB_MIN = 0
    RGB_MAX = 255
    
    def __init__(self):
        """Base constructor - subclasses should call super().__init__()"""
        self._r: int = 0
        self._g: int = 0  
        self._b: int = 0
    
    # === ABSTRACT METHODS (must be implemented by subclasses) ===
    
    @abstractmethod
    def to_rgb(self) -> 'RGB':
        """Convert to RGB representation."""
        pass
    
    @abstractmethod
    def to_hex(self) -> 'Hex':
        """Convert to Hex representation."""
        pass
    
    # === RGB COMPONENT ACCESS (common to all color types) ===
    
    @property
    def r(self) -> int:
        """Red component (0-255)."""
        return self._r
    
    @property
    def g(self) -> int:
        """Green component (0-255)."""
        return self._g
    
    @property
    def b(self) -> int:
        """Blue component (0-255)."""
        return self._b
    
    @property
    def rgb(self) -> Tuple[int, int, int]:
        """RGB components as tuple."""
        return (self._r, self._g, self._b)
    
    # === COLOR VALIDATION ===
    
    @staticmethod
    def _validate_color_value(value: Any, color_name: str = "color") -> int:
        """
        Validate and convert color value to integer in range [0, 255].
        
        Args:
            value: The color value to validate
            color_name: Name of the color component for error messages
            
        Returns:
            int: Valid color value
            
        Raises:
            TypeError: If value is not numeric
            ValueError: If value is outside valid range
        """
        if not isinstance(value, numbers.Real):
            raise TypeError(f"{color_name} value must be numeric, got {type(value).__name__}")
        
        int_value = int(value)
        
        if not (BaseColor.RGB_MIN <= int_value <= BaseColor.RGB_MAX):
            raise ValueError(f"{color_name} value must be in range [{BaseColor.RGB_MIN}, {BaseColor.RGB_MAX}], got {int_value}")
        
        return int_value
    
    @staticmethod
    def _validate_normalized_value(value: Any, color_name: str = "color") -> float:
        """
        Validate normalized color value in range [0.0, 1.0].
        
        Args:
            value: The normalized color value to validate
            color_name: Name of the color component for error messages
            
        Returns:
            float: Valid normalized color value
        """
        if not isinstance(value, numbers.Real):
            raise TypeError(f"{color_name} value must be numeric, got {type(value).__name__}")
        
        float_value = float(value)
        
        if not (0.0 <= float_value <= 1.0):
            raise ValueError(f"{color_name} value must be in range [0.0, 1.0], got {float_value}")
        
        return float_value
    
    # === COLOR SPACE CONVERSIONS ===
    
    def to_hsl(self) -> 'HSV':
        """Convert to HSL (Hue, Saturation, Lightness)."""
        r, g, b = self.normalized()
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Lightness
        lightness = (max_val + min_val) / 2.0
        
        if diff == 0:
            # Achromatic (gray)
            hue = saturation = 0.0
        else:
            # Saturation
            if lightness < 0.5:
                saturation = diff / (max_val + min_val)
            else:
                saturation = diff / (2.0 - max_val - min_val)
            
            # Hue
            if max_val == r:
                hue = ((g - b) / diff) % 6
            elif max_val == g:
                hue = (b - r) / diff + 2
            else:  # max_val == b
                hue = (r - g) / diff + 4
            
            hue *= 60  # Convert to degrees
        
        # Import here to avoid circular imports
        from .hsv import HSL
        return HSL(hue, saturation * 100, lightness * 100)
    
    def to_hsv(self) -> 'HSV':
        """Convert to HSV (Hue, Saturation, Value)."""
        r, g, b = self.normalized()
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Value
        value = max_val
        
        # Saturation
        saturation = 0.0 if max_val == 0 else diff / max_val
        
        # Hue
        if diff == 0:
            hue = 0.0
        elif max_val == r:
            hue = ((g - b) / diff) % 6
        elif max_val == g:
            hue = (b - r) / diff + 2
        else:  # max_val == b
            hue = (r - g) / diff + 4
        
        hue *= 60  # Convert to degrees
        
        # Import here to avoid circular imports
        from .hsv import HSV
        return HSV(hue, saturation * 100, value * 100)
    
    def normalized(self) -> Tuple[float, float, float]:
        """Return RGB values normalized to [0.0, 1.0] range."""
        return (
            self._r / 255.0,
            self._g / 255.0, 
            self._b / 255.0
        )
    
    # === COLOR MANIPULATION ===
    
    def lighten(self, factor: float) -> 'Self':
        """
        Return lightened version of color.
        
        Args:
            factor: Lightening factor (0.0 to 1.0)
            
        Returns:
            New color instance of same type, lightened
        """
        factor = max(0.0, min(1.0, factor))
        new_r = min(255, int(self._r + (255 - self._r) * factor))
        new_g = min(255, int(self._g + (255 - self._g) * factor))
        new_b = min(255, int(self._b + (255 - self._b) * factor))
        
        # Return same type as caller
        return self._create_from_rgb(new_r, new_g, new_b)
    
    def darken(self, factor: float) -> 'Self':
        """
        Return darkened version of color.
        
        Args:
            factor: Darkening factor (0.0 to 1.0)
            
        Returns:
            New color instance of same type, darkened
        """
        factor = max(0.0, min(1.0, factor))
        new_r = int(self._r * (1.0 - factor))
        new_g = int(self._g * (1.0 - factor))
        new_b = int(self._b * (1.0 - factor))
        
        return self._create_from_rgb(new_r, new_g, new_b)
    
    def invert(self) -> 'Self':
        """Return inverted (complement) color."""
        return self._create_from_rgb(255 - self._r, 255 - self._g, 255 - self._b)
    
    def grayscale(self) -> 'Self':
        """Convert to grayscale using luminance formula (ITU-R BT.709)."""
        # Using ITU-R BT.709 luma coefficients
        gray = int(0.2126 * self._r + 0.7152 * self._g + 0.0722 * self._b)
        return self._create_from_rgb(gray, gray, gray)
    
    def saturate(self, factor: float) -> 'Self':
        """
        Increase saturation by factor.
        
        Args:
            factor: Saturation increase factor (0.0 to 1.0)
        """
        hsl = self.to_hsl()
        new_saturation = min(100, hsl.s + (hsl.s * factor))
        return hsl.__class__(hsl.h, new_saturation, hsl.l).to_rgb()
    
    def desaturate(self, factor: float) -> 'Self':
        """
        Decrease saturation by factor.
        
        Args:
            factor: Saturation decrease factor (0.0 to 1.0)
        """
        hsl = self.to_hsl()
        new_saturation = max(0, hsl.s - (hsl.s * factor))
        return hsl.__class__(hsl.h, new_saturation, hsl.l).to_rgb()
    
    def adjust_hue(self, degrees: float) -> 'Self':
        """
        Adjust hue by specified degrees.
        
        Args:
            degrees: Degrees to adjust hue (-360 to 360)
        """
        hsl = self.to_hsl()
        new_hue = (hsl.h + degrees) % 360
        return hsl.__class__(new_hue, hsl.s, hsl.l).to_rgb()
    
    # === COLOR ANALYSIS ===
    
    def luminance(self) -> float:
        """
        Calculate relative luminance (0.0 to 1.0).
        Uses sRGB colorimetric definition.
        """
        def linearize(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        r_lin = linearize(self._r)
        g_lin = linearize(self._g)
        b_lin = linearize(self._b)
        
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    
    # === SEQUENCE PROTOCOL ===
    
    def __iter__(self) -> Iterator[int]:
        """Iterate over RGB components."""
        yield self._r
        yield self._g
        yield self._b
    
    def __getitem__(self, index: int) -> int:
        """Support indexing for RGB components."""
        if index == 0:
            return self._r
        elif index == 1:
            return self._g
        elif index == 2:
            return self._b
        else:
            raise IndexError("Color index out of range (0-2)")
    
    def __len__(self) -> int:
        """Return length of 3 for RGB components."""
        return 3
    
    # === EQUALITY AND COMPARISON ===
    
    def __eq__(self, other: Any) -> bool:
        """Check equality based on RGB values."""
        if not isinstance(other, BaseColor):
            return NotImplemented
        return (self._r, self._g, self._b) == (other._r, other._g, other._b)
    
    def __hash__(self) -> int:
        """Make color hashable based on RGB values."""
        return hash((self._r, self._g, self._b))
    
    # === STRING REPRESENTATIONS ===
    
    def __str__(self) -> str:
        """Default string representation - subclasses should override."""
        return f"{self.__class__.__name__}({self._r}, {self._g}, {self._b})"
    
    def __repr__(self) -> str:
        """Developer representation - subclasses should override."""
        return f"{self.__class__.__name__}({self._r}, {self._g}, {self._b})"
    
    # === CONVERSION UTILITIES ===
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple."""
        return (self._r, self._g, self._b)
    
    def to_list(self) -> list:
        """Convert to RGB list."""
        return [self._r, self._g, self._b]
    
    def to_dict(self) -> dict:
        """Convert to dictionary with RGB keys."""
        return {'r': self._r, 'g': self._g, 'b': self._b}
    
    # === CSS/WEB FORMATS ===
    
    def css_rgb(self) -> str:
        """CSS rgb() format: rgb(255, 128, 64)"""
        return f"rgb({self._r}, {self._g}, {self._b})"
    
    def css_rgba(self, alpha: float = 1.0) -> str:
        """CSS rgba() format: rgba(255, 128, 64, 1.0)"""
        alpha = max(0.0, min(1.0, alpha))
        return f"rgba({self._r}, {self._g}, {self._b}, {alpha})"