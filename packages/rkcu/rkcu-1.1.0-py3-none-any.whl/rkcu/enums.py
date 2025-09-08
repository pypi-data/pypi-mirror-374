from enum import Enum

class Speed(Enum):
    SPEED_1 = 0x01
    SPEED_2 = 0x02
    SPEED_3 = 0x03
    SPEED_4 = 0x04
    SPEED_5 = 0x05

    @staticmethod
    def from_value(value: int):
        values = {
            1: Speed.SPEED_1,
            2: Speed.SPEED_2,
            3: Speed.SPEED_3,
            4: Speed.SPEED_4,
            5: Speed.SPEED_5,
        }
        if value in list(values.keys()):
            return values[value]
        else :
            print("warning: unable to find specified speed, using Speed 5")
            return Speed.SPEED_5 # default value

class Brightness(Enum):
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5

    @staticmethod
    def from_value(value: int):
        if 0 <= value <= 5:
            levels = {
                0: Brightness.LEVEL_0,
                1: Brightness.LEVEL_1,
                2: Brightness.LEVEL_2,
                3: Brightness.LEVEL_3,
                4: Brightness.LEVEL_4,
                5: Brightness.LEVEL_5,
            }
            return levels[value]
        else:
            print(f"warning: unable to find specified brightness, using Brightness 5")
            return Brightness.LEVEL_5 # default value

class RainbowMode(Enum):
    OFF = 0x00
    ON = 0x01

    @staticmethod
    def from_value(value: bool):
        if value:
            return RainbowMode.ON
        else :
            return RainbowMode.OFF

class Sleep(Enum):
    SLEEP_5_MIN = 0x01
    SLEEP_10_MIN = 0x02
    SLEEP_20_MIN = 0x03
    SLEEP_30_MIN = 0x04
    SLEEP_NEVER = 0x05

    @staticmethod
    def from_value(value: int):
        values = {
            1: Sleep.SLEEP_5_MIN,
            2: Sleep.SLEEP_10_MIN,
            3: Sleep.SLEEP_20_MIN,
            4: Sleep.SLEEP_30_MIN,
            5: Sleep.SLEEP_NEVER,
        }
        if value in list(values.keys()):
            return values[value]
        else :
            print("warning: unable to find specified sleep value, using Never Sleep")
            return Sleep.SLEEP_NEVER # default value

class Animation(Enum):
    NEON_STREAM = 1       # RGBModes::NeonStream = 1
    RIPPLES_SHINING = 2   # RGBModes::RipplesShining = 2
    ROTATING_WINDMILL = 3 # RGBModes::RotatingWindmill = 3
    SINE_WAVE = 4         # RGBModes::SineWave = 4
    RAINBOW_ROULETTE = 5  # RGBModes::RainbowRoulette = 5
    STARS_TWINKLE = 6     # RGBModes::StarsTwinkle = 6
    LAYER_UPON_LAYER = 7  # RGBModes::LayerUponLayer = 7
    RICH_AND_HONORED = 8  # RGBModes::RichAndHonored = 8
    MARQUEE_EFFECT = 9    # RGBModes::MarqueeEffect = 9
    ROTATING_STORM = 10   # RGBModes::RotatingStorm = 10
    SERPENTINE_HORSE = 11 # RGBModes::SerpentineHorseRace = 11
    RETRO_SNAKE = 12      # RGBModes::RetroSnake = 12
    DIAGONAL_TRANSFORMER = 13  # RGBModes::DiagonalTransformation = 13
    CUSTOM = 14           # RGBModes::Custom = 14
    AMBILIGHT = 15        # RGBModes::Ambilight = 15
    STREAMER = 16         # RGBModes::Streamer = 16
    STEADY = 17           # RGBModes::Steady = 17
    BREATHING = 18        # RGBModes::Breathing = 18
    NEON = 19             # RGBModes::Neon = 19
    SHADOW_DISAPPEAR = 20 # RGBModes::ShadowDisappear = 20
    FLASH_AWAY = 21       # RGBModes::FlashAway = 21

    @staticmethod
    def from_value(value: str):
        values = {
            "neon_stream": Animation.NEON_STREAM,
            "ripples_shining": Animation.RIPPLES_SHINING,
            "sine_wave": Animation.SINE_WAVE,
            "rainbow_routlette": Animation.RAINBOW_ROULETTE,
            "stars_twinkle": Animation.STARS_TWINKLE,
            "layer_upon_layer": Animation.LAYER_UPON_LAYER,
            "rich_and_honored": Animation.RICH_AND_HONORED,
            "marquee_effect": Animation.MARQUEE_EFFECT,
            "rotating_storm": Animation.ROTATING_STORM,
            "serpentine_horse": Animation.SERPENTINE_HORSE,
            "retro_snake": Animation.RETRO_SNAKE,
            "diagonal_transformer": Animation.DIAGONAL_TRANSFORMER,
            "ambilight": Animation.AMBILIGHT,
            "streamer": Animation.STREAMER,
            "steady": Animation.STEADY,
            "breathing": Animation.BREATHING,
            "neon": Animation.NEON,
            "shadow_disappear": Animation.SHADOW_DISAPPEAR,
            "flash_away": Animation.FLASH_AWAY
        }
        if value in list(values.keys()):
            return values[value]
        else :
            print("warning: unable to find specified animation, using Neon Stream")
            return Animation.NEON_STREAM # default value
    
    @staticmethod
    def list_animations():
        animations = [anim.name.lower() for anim in Animation]
        return animations