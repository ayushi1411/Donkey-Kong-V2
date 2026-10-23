from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    # screen settings
    SCREEN_WIDTH: int = 1280
    SCREEN_HEIGHT: int = 500
    TILE_SIZE: int = 16
    WORLD_WIDTH: int = 200 * 16

    #game rule settings
    MAX_LEVEL: int = 10
    COIN_SCORE: int = 10
    COIN_FOR_LIFE: int = 100

    #physics and movement settings
    GRAVITY: float = 0.5
    JUMP_POWER: float = -10
    PLAYER_SPEED: float = 3
    ANIMATION_SPEED: int = 5
    PLAYER_START_X: int = 100
    PLAYER_START_Y: int = 100

    #colour settings
    BLACK: tuple = (0, 0, 0)




