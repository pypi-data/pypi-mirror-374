
from typing import Iterable, Tuple, TYPE_CHECKING
from .color import BaseColor

if TYPE_CHECKING:
    from .hex import Hex
    from .hsv import HSV

class RGB(BaseColor):
    def __init__(self, *args):
        super().__init__()  # Initialize BaseColor
        
        if len(args) == 0:
            # Default to black
            self._r, self._g, self._b = 0, 0, 0
        elif len(args) == 1:
            self._init_single_arg(args[0])
        elif len(args) == 3:
            self._init_three_args(*args)
        else:
            raise ValueError(f"RGB() takes 0, 1, or 3 arguments ({len(args)} given)")
    
    def _init_single_arg(self, arg):
        if isinstance(arg, RGB):
            # Copy constructor
            self._r, self._g, self._b = arg._r, arg._g, arg._b
        elif isinstance(arg, str):
            # Parse string like "255,128,0"
            self._init_str(arg)
        elif hasattr(arg, '__iter__') and not isinstance(arg, (str, bytes)):
            # Handle iterables (list, tuple, etc.)
            self._init_iter(arg)
        else:
            raise TypeError(f"Cannot initialize RGB from {type(arg).__name__}")
    
    def _init_str(self, color_str: str):
        try:
            values = [int(x.strip()) for x in color_str.split(',')]
            if len(values) != 3:
                raise ValueError("String must contain exactly 3 comma-separated values")
            self._init_three_args(*values)
        except ValueError as e:
            raise ValueError(f"Invalid RGB string format: {e}")
    
    def _init_iter(self, iterable):
        try:
            values = list(iterable)
            if len(values) != 3:
                raise ValueError(f"Iterable must contain exactly 3 values, got {len(values)}")
            self._init_three_args(*values)
        except TypeError:
            raise TypeError("Argument must be iterable")
    
    def _init_three_args(self, r, g, b):
        # Use BaseColor's validation method
        self._r = self._validate_color_value(r, 'red')
        self._g = self._validate_color_value(g, 'green')
        self._b = self._validate_color_value(b, 'blue')
    
    # Remove the duplicate _validate_color_value method - use BaseColor's version
    
    def _get_component(self, char: str) -> int:
        """Get color component by swizzle character."""
        if char == 'r':
            return self._r
        elif char == 'g':
            return self._g
        elif char == 'b':
            return self._b
        else:
            raise ValueError(f"Invalid swizzle character: {char}")
    
    def _set_component(self, char: str, value: int):
        """Set color component by swizzle character."""
        validated_value = self._validate_color_value(value, char)
        if char == 'r':
            self._r = validated_value
        elif char == 'g':
            self._g = validated_value
        elif char == 'b':
            self._b = validated_value
        else:
            raise ValueError(f"Invalid swizzle character: {char}")
    
    def __getattr__(self, name: str):
        """Handle GLSL-style swizzling access like .rgb, .rg, .rrg, etc."""
        # Check if it's a valid swizzle pattern
        if all(c in 'rgb' for c in name):
            if len(name) == 1:
                # Single component: .r, .g, .b
                return self._get_component(name)
            else:
                # Multiple components: .rgb, .rg, .gbr, .rrg, etc.
                return tuple(self._get_component(c) for c in name)
        
        # If not a swizzle pattern, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value):
        """Handle GLSL-style swizzling assignment like .rgb = (255, 128, 0)."""
        # Handle private attributes normally
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        
        # Check if it's a valid swizzle pattern
        if all(c in 'rgb' for c in name):
            if len(name) == 1:
                # Single component assignment: .r = 255
                self._set_component(name, value)
            else:
                # Multiple component assignment: .rgb = (255, 128, 0)
                if not hasattr(value, '__iter__') or isinstance(value, (str, bytes)):
                    raise TypeError(f"Cannot assign {type(value).__name__} to swizzle pattern '{name}'")
                
                values = list(value)
                if len(values) != len(name):
                    raise ValueError(f"Cannot assign {len(values)} values to {len(name)} components")
                
                for char, val in zip(name, values):
                    self._set_component(char, val)
        else:
            # If not a swizzle pattern, handle normally
            super().__setattr__(name, value)
    
    # Keep your existing properties for compatibility, but BaseColor also provides r, g, b, rgb
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
        """RGB values as a tuple."""
        return (self._r, self._g, self._b)
    
    # Property setters for direct assignment
    @r.setter
    def r(self, value: int):
        """Set red component."""
        self._r = self._validate_color_value(value, 'red')
    
    @g.setter
    def g(self, value: int):
        """Set green component."""
        self._g = self._validate_color_value(value, 'green')
    
    @b.setter
    def b(self, value: int):
        """Set blue component."""
        self._b = self._validate_color_value(value, 'blue')
    
    @rgb.setter
    def rgb(self, value: Iterable[int]):
        """Set RGB components from iterable."""
        values = list(value)
        if len(values) != 3:
            raise ValueError(f"RGB requires exactly 3 values, got {len(values)}")
        self._r, self._g, self._b = [self._validate_color_value(v, ['red', 'green', 'blue'][i]) 
                                     for i, v in enumerate(values)]
    
    # === ABSTRACT METHOD IMPLEMENTATIONS ===
    
    def to_rgb(self) -> 'RGB':
        """Convert to RGB representation (returns self since this is RGB)."""
        return self
    
    def to_hex(self) -> 'Hex':
        """Convert to Hex representation."""
        from .hex import Hex
        return Hex.from_rgb(self._r, self._g, self._b)
    
    # === OVERRIDE BASE CLASS HELPER ===
    
    def _create_from_rgb(self, r: int, g: int, b: int) -> 'RGB':
        """Create new RGB instance from RGB values."""
        return RGB(r, g, b)
    
    # Remove duplicate methods that are already in BaseColor:
    # - __iter__, __getitem__, __len__ (BaseColor provides these)
    # - __eq__, __hash__ (BaseColor provides these)
    # - to_tuple(), to_list(), normalized() (BaseColor provides these)
    
    # Keep RGB-specific methods
    def with_red(self, r: int) -> 'RGB':
        """Return new RGB instance with modified red component."""
        return RGB(r, self._g, self._b)
    
    def with_green(self, g: int) -> 'RGB':
        """Return new RGB instance with modified green component."""
        return RGB(self._r, g, self._b)
    
    def with_blue(self, b: int) -> 'RGB':
        """Return new RGB instance with modified blue component."""
        return RGB(self._r, self._g, b)
    
    # Keep your string representations (override BaseColor's default)
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"RGB({self._r}, {self._g}, {self._b})"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"RGB({self._r}, {self._g}, {self._b})"
    
    # Class methods for alternative constructors
    @classmethod
    def from_hex(cls, hex_string: str) -> 'RGB':
        """
        Create RGB from hexadecimal string.
        
        Args:
            hex_string: Hex color like "#ff8000" or "ff8000"
            
        Returns:
            RGB: New RGB instance
        """
        if isinstance(hex_string, str):
            hex_string = hex_string.lstrip('#')
            if len(hex_string) != 6:
                raise ValueError("Hex string must be 6 characters long")
            
            try:
                r = int(hex_string[0:2], 16)
                g = int(hex_string[2:4], 16)
                b = int(hex_string[4:6], 16)
                return cls(r, g, b)
            except ValueError:
                raise ValueError("Invalid hexadecimal color string")
    
    @classmethod
    def from_normalized(cls, r: float, g: float, b: float) -> 'RGB':
        """
        Create RGB from normalized [0.0, 1.0] values.
        
        Args:
            r, g, b: Normalized color values
            
        Returns:
            RGB: New RGB instance
        """
        return cls(int(r * 255), int(g * 255), int(b * 255))