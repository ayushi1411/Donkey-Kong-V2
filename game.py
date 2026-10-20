import sys
import pygame
from settings import *
from sprites import Player

class Game:
    def __init__(self):
        pygame.display.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
        pygame.display.set_caption("Donkey Kong")
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        self.player = Player(self.settings.PLAYER_START_X, self.settings.PLAYER_START_Y)
        self.all_sprites.add(self.player)

    def run(self):
        while self.running:
           self.events()
           self.update()
           self.draw()
           self.clock.tick(60)


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(self.settings.BLACK)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()