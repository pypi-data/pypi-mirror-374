import argparse
import json
import sys

from .config import get_base_config
from .utils import RKCU
from .enums import Animation

# Python based Command Line wrapper for managing profiles on Royal Kludge keyboards
# author: Hardik Srivastava [oddlyspaced]
# changes: Gagan K [gagan16k]

parser = argparse.ArgumentParser(
    prog = 'RKCU - Royal Kludge Config Utility',
    description = 'Utility to manage profiles on Royal Kludge keyboards with per-key RGB support.'
)

color_config = get_base_config()

def setup_arg_parser():
    global parser
    parser.add_argument('--speed', '-sp', help='Animation speed (1-5)')
    parser.add_argument('--brightness', '-br', help='Brightness level (0-255)')
    parser.add_argument('--sleep', '-sl', help='Sleep timeout (1-5: 5min/10min/20min/30min/never)')

    parser.add_argument('--animation', '-an', help='Animation type')
    parser.add_argument('--list-animations', '-la', action='store_true', help='List available animations and exit')

    parser.add_argument('--rainbow', '-rb', action='store_true', help='Enable rainbow mode')

    parser.add_argument('--red', '-r', help='Red color value (0-255)')
    parser.add_argument('--green', '-g', help='Green color value (0-255)')
    parser.add_argument('--blue', '-b', help='Blue color value (0-255)')
    parser.add_argument('--color', '-c', help='RGB color value in hex format (e.g., ff0000 for red)')
    
    # Per-key RGB options
    parser.add_argument('--set-key', action='append', help='Set color for a specific key: KEY_INDEX:RRGGBB (can be used multiple times)')
    parser.add_argument('--set-keys-json', help='Set multiple key colors from JSON file')
    parser.add_argument('--clear-custom', action='store_true', help='Clear all custom per-key colors')

def read_args():
    args = parser.parse_args()
    var = vars(args)

    # Handle list animations
    if args.list_animations:
        anims=Animation.list_animations()
        for anim in anims:
            print(anim)
        sys.exit(0)

    # Handle hex color conversion
    if args.color:
        try:
            hex_color = args.color.lstrip('#')
            if len(hex_color) != 6:
                raise ValueError("Hex color must be 6 characters (e.g., 'ff0000' for red)")
            
            red = int(hex_color[0:2], 16)
            green = int(hex_color[2:4], 16)
            blue = int(hex_color[4:6], 16)
            
            var['red'] = red
            var['green'] = green
            var['blue'] = blue
            
            print(f"Set RGB color from hex #{hex_color}: R={red}, G={green}, B={blue}")
        except ValueError as e:
            print(f"Error parsing hex color '{args.color}': {e}")
            return

    # Handle clear custom colors
    if args.clear_custom:
        color_config.PER_KEY_RGB.clear_all()
        print("Cleared all custom per-key colors")
    
    # Handle per-key color setting
    if args.set_key:
        for set_key_arg in args.set_key:
            try:
                key_color = set_key_arg.split(':')
                if len(key_color) != 2:
                    raise ValueError("Format should be KEY_INDEX:RRGGBB")
                
                key_index = int(key_color[0])
                hex_color = key_color[1]
                
                color_config.PER_KEY_RGB.set_key_color_hex(key_index, hex_color)
                print(f"Set key {key_index} to color #{hex_color}")
            except Exception as e:
                print(f"Error setting key color for '{set_key_arg}': {e}")
                return
    
    # Handle JSON file input
    if args.set_keys_json:
        try:
            with open(args.set_keys_json, 'r') as f:
                keys_data = json.load(f)
            
            for key_index, hex_color in keys_data.items():
                try:
                    key_idx = int(key_index)
                    color_config.PER_KEY_RGB.set_key_color_hex(key_idx, hex_color)
                    print(f"Set key {key_idx} to color #{hex_color}")
                except ValueError:
                    continue
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return
    
    update_config(var)

def update_config(var: dict):
    color_config.update(var)

def main():
    setup_arg_parser()
    read_args()

    if not any(arg in sys.argv for arg in ['--list-keys', '--list-animations', '-la', '-h', '--help']):
        rk = RKCU(0x258a, 0x00e0)
        rk.apply_config(color_config)
        print("Configuration applied successfully!")
        
        if color_config.PER_KEY_RGB.has_custom_colors():
            print(f"Applied custom colors to {len(color_config.PER_KEY_RGB.custom_colors)} keys")

if __name__ == "__main__":
    main()
