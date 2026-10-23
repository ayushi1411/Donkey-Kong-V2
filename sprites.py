import pygame
from settings import *
import random

class Character(pygame.sprite.Sprite):
    """Base class for all moving characters. Provides a set_image() helper
    that anchors to midbottom on every frame swap, keeping feet planted
    and preventing jitter caused by frames of different dimensions."""
    def set_image(self, image):
        old_midbottom = self.rect.midbottom
        self.image = image
        self.rect = self.image.get_rect(midbottom=old_midbottom)
        if hasattr(self, 'float_y'):
            self.float_y = float(self.rect.y)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width = 96, height = 32):
        super().__init__()
        raw_image = pygame.image.load('assets/platform.png').convert_alpha()
        self.image = pygame.transform.scale(raw_image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

class Ladder(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/ladder_sprite_2.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

class BrokenLadder(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img_num = random.randint(1, 5)
        self.image = pygame.image.load(f'assets/broken_ladder_sprite_{img_num}.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/exit.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

class Queen(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/cage_closed.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(Character):
    def __init__(self, x, y, physics):
        super().__init__()
        self.physics = physics #store reference to the physics helper
        self.idle_image_right = pygame.image.load('assets/player_idle_right.png').convert_alpha()
        self.idle_image_left = pygame.transform.flip(self.idle_image_right, True, False)
        self.image = self.idle_image_right

        self.run_right_frames = []
        for i in range(1, 11):
            frame = pygame.image.load(f'assets/player_run_right_{i}.png').convert_alpha()
            self.run_right_frames.append(frame)
        self.run_left_frames = []
        for right_frame in self.run_right_frames:
            left_frame = pygame.transform.flip(right_frame, True, False)
            self.run_left_frames.append(left_frame)
        self.jump_right_frames = []
        for i in range(1, 6):
            frame = pygame.image.load(f'assets/player_jump_right_{i}.png').convert_alpha()
            self.jump_right_frames.append(frame)
        self.jump_left_frames = []
        for right_frame in self.jump_right_frames:
            left_frame = pygame.transform.flip(right_frame, True, False)
            self.jump_left_frames.append(left_frame)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.settings = Settings()
        self.vel_x = 0
        self.vel_y = 0
        self.float_y = float(self.rect.y)  # Use float for smoother vertical movement
        self.current_frame = 0
        self.animation_timer = 0
        self.facing_right = True
        self.is_jumping = False

    def update(self):
        keys = pygame.key.get_pressed()

        # --- Jump Input ---
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.vel_y = self.settings.JUMP_POWER
            self.is_jumping = True

        # --- Gravity ---
        self.vel_y += self.settings.GRAVITY
        self.float_y += self.vel_y
        self.rect.y = int(self.float_y)

        # --- Temporary Floor Clamp (until platform collision is built) ---
        if self.rect.bottom >= self.settings.SCREEN_HEIGHT:
            self.rect.bottom = self.settings.SCREEN_HEIGHT
            self.float_y = float(self.rect.y) # keep float_y in sync with rect.y
            self.vel_y = 0
            self.is_jumping = False

        # --- Horizontal Movement ---
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.settings.PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vel_x = self.settings.PLAYER_SPEED
            self.facing_right = True
        self.rect.x += self.vel_x

        self.physics.check_horizontal_collision(self)  # Check for horizontal collisions with platforms

        # --- Animation (jump takes highest priority) ---
        if self.is_jumping:
            num_frames = len(self.jump_right_frames)
            mid = num_frames // 2
            if self.vel_y < 0:
                # Ascending: map vel_y from JUMP_POWER→0 across first half of frames
                ratio = (self.vel_y - self.settings.JUMP_POWER) / (0 - self.settings.JUMP_POWER)
                frame_index = min(int(ratio * (mid + 1)), mid)
            else:
                # Descending: map vel_y from 0→JUMP_POWER magnitude across second half
                ratio = min(self.vel_y / abs(self.settings.JUMP_POWER), 1.0)
                frame_index = min(mid + int(ratio * (num_frames - mid)), num_frames - 1)
            frames = self.jump_right_frames if self.facing_right else self.jump_left_frames
            self.set_image(frames[frame_index])
        elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.animation_timer += 1
            if self.animation_timer >= self.settings.ANIMATION_SPEED:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.run_right_frames)
            frames = self.run_right_frames if self.facing_right else self.run_left_frames
            self.set_image(frames[self.current_frame])
        else:
            self.current_frame = 0
            self.animation_timer = 0
            self.set_image(self.idle_image_right if self.facing_right else self.idle_image_left)
