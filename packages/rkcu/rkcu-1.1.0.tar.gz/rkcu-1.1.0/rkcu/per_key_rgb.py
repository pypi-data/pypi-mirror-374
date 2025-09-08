"""
Per-key RGB functionality based on rangoli project implementation.
Allows setting individual RGB colors for each key on the keyboard.
"""
from typing import Dict, Tuple

class PerKeyRGB:
    """Manages per-key RGB lighting configuration."""
    
    def __init__(self):
        self.custom_colors: Dict[int, Tuple[int, int, int]] = {}
    
    def set_key_color(self, key_index: int, red: int, green: int, blue: int):
        """Set RGB color for a specific key."""
        if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
            raise ValueError("RGB values must be between 0 and 255")
        
        self.custom_colors[key_index] = (red, green, blue)
    
    def set_key_color_hex(self, key_index: int, hex_color: str):
        """Set RGB color for a specific key using hex color code."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters (e.g., 'ff0000' for red)")
        
        try:
            red = int(hex_color[0:2], 16)
            green = int(hex_color[2:4], 16)
            blue = int(hex_color[4:6], 16)
            self.set_key_color(key_index, red, green, blue)
        except ValueError:
            raise ValueError("Invalid hex color format")
    
    def clear_key(self, key_index: int):
        """Remove custom color for a specific key."""
        if key_index in self.custom_colors:
            del self.custom_colors[key_index]
    
    def clear_all(self):
        """Remove all custom colors."""
        self.custom_colors.clear()
    
    def has_custom_colors(self) -> bool:
        """Check if any custom colors are set."""
        return len(self.custom_colors) > 0
    
    def get_custom_light_buffers(self) -> list:
        """Generate the custom light mode buffers for the keyboard."""
        if not self.has_custom_colors():
            return []
        
        BUFFER_SIZE = 65
        CUSTOM_LIGHT_BUFFERS_SIZE = 7
        
        led_full_buffer = bytearray(CUSTOM_LIGHT_BUFFERS_SIZE * BUFFER_SIZE)
        
        for key_index, (red, green, blue) in self.custom_colors.items():
            lbi = key_index * 3
            if lbi + 2 < len(led_full_buffer):
                led_full_buffer[lbi] = red
                led_full_buffer[lbi + 1] = green
                led_full_buffer[lbi + 2] = blue
        
        buffers = []
        led_buffer_index = 0
        
        for i in range(CUSTOM_LIGHT_BUFFERS_SIZE):
            buffer = bytearray(BUFFER_SIZE)
            buffer[0] = 0x0a
            buffer[1] = CUSTOM_LIGHT_BUFFERS_SIZE
            buffer[2] = i + 1
            
            if i == 0:
                buffer[3] = 0x03
                buffer[4] = 0x7e
                buffer[5] = 0x01
                start_index = 6
            else:
                start_index = 3
            
            for buffer_index in range(start_index, BUFFER_SIZE):
                if led_buffer_index < len(led_full_buffer):
                    buffer[buffer_index] = led_full_buffer[led_buffer_index]
                    led_buffer_index += 1
            
            buffers.append(buffer)
        
        return buffers