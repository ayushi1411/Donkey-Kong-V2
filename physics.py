import pygame

class Physics:
    def __init__(self, platforms):
        self.platforms = platforms

    def check_horizontal_collision(self, character):
        hits = pygame.sprite.spritecollide(character, self.platforms, False)
        for platform in hits:
            if character.vel_x > 0:  # moving right -> hit left side of the platform
                character.rect.right = platform.rect.left
            elif character.vel_x < 0:  # moving left -> hit right side of the platform
                character.rect.left = platform.rect.right
        return bool(hits)