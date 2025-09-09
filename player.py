import pygame

class Player:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/sprites/player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 4
        self.direction = pygame.Vector2(0, 0)

    def handle_event(self, event):
        pass  # we'll use key states instead of event-based

    def update(self):
        keys = pygame.key.get_pressed()
        self.direction.x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        self.direction.y = keys[pygame.K_DOWN] - keys[pygame.K_UP]

        # Normalize diagonal movement
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)
