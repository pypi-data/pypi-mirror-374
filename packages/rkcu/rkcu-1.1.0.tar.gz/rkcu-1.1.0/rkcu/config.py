from dataclasses import dataclass
from .enums import Animation, Speed, Brightness, RainbowMode, Sleep
from .per_key_rgb import PerKeyRGB

# data class of base config for usb report 
@dataclass
class Config:
    ANIMATION_TYPE: Animation
    ANIMATION_SPEED: Speed
    ANIMATION_BRIGHTNESS: Brightness
    ANIMATION_GREEN: int
    ANIMATION_RED: int
    ANIMATION_BLUE: int
    ANIMATION_RAINBOW: RainbowMode
    ANIMATION_SLEEP_DURATION: Sleep
    PER_KEY_RGB: PerKeyRGB

    def __init__(self, animation: Animation, speed: Speed, brightness: Brightness, red: int, green: int, blue: int, is_rainbow: RainbowMode, sleep: Sleep, per_key_rgb: PerKeyRGB = None) -> None:
        self.ANIMATION_TYPE = animation
        self.ANIMATION_SPEED = speed
        self.ANIMATION_BRIGHTNESS = brightness.value
        self.ANIMATION_RED = red
        self.ANIMATION_GREEN = green
        self.ANIMATION_BLUE = blue
        self.ANIMATION_RAINBOW = is_rainbow
        self.ANIMATION_SLEEP_DURATION = sleep
        self.PER_KEY_RGB = per_key_rgb if per_key_rgb is not None else PerKeyRGB()
    
    def update(self, var: dict):
        self.ANIMATION_TYPE = Animation.from_value("neon_stream" if var['animation'] is None else var['animation'])
        self.ANIMATION_SPEED = Speed.from_value(5 if var['speed'] is None else int(var['speed']))
        raw_brightness = 5 if var['brightness'] is None else int(var['brightness'])
        self.ANIMATION_BRIGHTNESS = Brightness.from_value(raw_brightness).value
        self.ANIMATION_RED = int(255 if var['red'] is None else var['red'])
        self.ANIMATION_GREEN = int(255 if var['green'] is None else var['green'])
        self.ANIMATION_BLUE = int(255 if var['blue'] is None else var['blue'])
        self.ANIMATION_RAINBOW = RainbowMode.from_value(var['rainbow'])
        self.ANIMATION_SLEEP_DURATION = Sleep.from_value(5 if var['sleep'] is None else int(var['sleep']))

    def report(self) -> bytearray:
        if self.PER_KEY_RGB.has_custom_colors():
            animation_mode = Animation.CUSTOM.value
        else:
            animation_mode = self.ANIMATION_TYPE.value
        
        report = bytearray(65)
        report[0] = 0x0a
        report[1] = 0x01
        report[2] = 0x01
        report[3] = 0x02
        report[4] = 0x29
        report[5] = animation_mode
        # report[6] is unused (0x00)
        report[7] = self.ANIMATION_SPEED.value
        report[8] = self.ANIMATION_BRIGHTNESS
        report[9] = self.ANIMATION_RED
        report[10] = self.ANIMATION_GREEN
        report[11] = self.ANIMATION_BLUE
        report[12] = self.ANIMATION_RAINBOW.value
        report[13] = self.ANIMATION_SLEEP_DURATION.value

        return report
    
    def get_custom_light_buffers(self) -> list:
        """Get per-key RGB buffers if custom colors are set."""
        return self.PER_KEY_RGB.get_custom_light_buffers()

def get_base_config() -> Config:
    config = Config(
        Animation.NEON_STREAM,
        Speed.SPEED_5,
        Brightness.LEVEL_0,  # Use brightness level 0
        255,
        255,
        255,
        RainbowMode.OFF,
        Sleep.SLEEP_5_MIN
    )
    return config