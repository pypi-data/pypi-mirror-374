
# RKCU - Royal Kludge Config Utility
Python3 based command line utility/API to manage and modify profiles on Royal Kludge keyboards with **per-key RGB support**.

## Features
- **Per-Key RGB Lighting**: Set individual colors for each key
- **JSON Configuration**: Load complex lighting setups from files
- **Windows Compatible**: Updated for Windows HID interface detection
- **RK100 Support**: Enhanced for newer Royal Kludge models
- **Rangoli**: Based on the [rangoli project](https://github.com/rnayabed/rangoli)

## Supported Keyboards
- Royal Kludge RK100 (VID: 0x258a, PID: 0x00e0)
- Royal Kludge RK61 (original support)
- Other RK keyboards with compatible HID interfaces

## Dependencies

    hidapi

## Standard Usage

    python rkcu.py <arguments>

Arguments :

    --speed, --sp [1-5]
    # speed of led animation.
    
    --brightness, -br [0-5]
    # brightness of led animation
	
	--sleep, -sl [1-5]
	# sleep duration for the keyboard led
	 - 1: 05 Minutes
	 - 2: 10 Minutes
	 - 3: 20 Minutes
	 - 4: 30 Minutes
	 - 5: Never Sleep
	
	--rainbow, -rb
	# Set LED color mode to Rainbow
	
	--red, -r 0-255
	# Red value of Color
	
	--green, -g 0-255
	# Green value of Color
	
	--blue, -b 0-255
	# Blue value of Color

	--color, -c "#RRGGBB"
	# Set color using hex format (e.g., "#ff0000" for red)
	# Note: This will override individual --red, --green, --blue values if provided.
	
	--animation, -an "animation_name"
	# List of availaible animations:
	 - neon_stream
	 - ripples_shining
	 - sine_wave
	 - rainbow_routlette
	 - stars_twinkle
	 - layer_upon_layer
	 - rich_and_honored
	 - marquee_effect
	 - rotating_storm
	 - serpentine_horse
	 - retro_snake
	 - diagonal_transformer
	 - ambilight
	 - streamer
	 - steady
	 - breathing
	 - neon
	 - shadow_disappear
	 - flash_away

	--list-animations, -la
	# List all supported animation names and exit

## Per-Key RGB Arguments

	--set-key KEY_INDEX:RRGGBB
	# Set color for a specific key (can be used multiple times)
	# Example: --set-key 15:ff0000 (sets key 15 to red)
	
	--set-keys-json FILE_PATH
	# Load multiple key colors from JSON file
	
	--clear-custom
	# Clear all custom per-key colors

Example :

    # Standard usage
    python rkcu.py --speed 3 --brightness 5 --sleep 5 -r 255 -g 255 -b 255 -an "ripples_shining"
    python rkcu.py -sp 5 -an "rotating_storm" -rb
    
    # Per-key RGB examples
    python rkcu.py --set-key 15:ff0000 --set-key 29:00ff00 
    python rkcu.py --set-keys-json rainbow_config.json      # Load from file
    python rkcu.py --set-key 15:ff0000 --brightness 2     # Custom key with brightness

## Custom Testing

Readme with some standard tests for keyboard (mainly per-key) RGB functionality can be found in [`custom_testing/README.md`](custom_testing/README.md).

## Notes

The `--rainbow` argument will overrule the `--red, --green, --blue` parameters.

By default the script would require superuser access to run. In order to run this without root, you can plug a udev rule by performing the following steps :
Step 1: Find your vendor id and product id. Here it is `258a` and `004a` respectively, and would most likely be same for you if you are having the same keyboard.

    $ lsusb
    Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 001 Device 005: ID 0c45:671e Microdia Integrated_Webcam_HD
    Bus 001 Device 002: ID 258a:004a SINO WEALTH RK Bluetooth Keyboard
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

Step 2:
add a `rules` file to `/etc/udev/rules.d`
file: `60-rk.rules`

    SUBSYSTEMS=="usb|hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="004a", TAG+="uaccess"

replace `258a` with your vendor id and `004a` with your product id, in case it is different.
Step 3:
Finally, reload your udev rules by running the following command :

    # udevadm control --reload-rules && udevadm trigger

## What's working?
Currently the script allows setting and configuring of inbuilt color profiles on the keyboard. Custom customisation such as custom LED colors and macros are still not present but will (hopefully) be soon supported.

## Credits
Big credits to [this](https://gitlab.com/CalcProgrammer1/OpenRGB/-/issues/2308) issue thread on the OpenRGB Gitlab Repo that served great reference.

Special thanks to the [Rangoli project](https://github.com/rnayabed/rangoli) for the foundational work that made the per-key RGB functionality possible.