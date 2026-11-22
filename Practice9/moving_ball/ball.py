import pygame

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def move(self, dx, dy, screen_w, screen_h):
        new_x = self.x + dx
        new_y = self.y + dy
        if self.radius <= new_x <= screen_w - self.radius:
            self.x = new_x
        if self.radius <= new_y <= screen_h - self.radius:
            self.y = new_y

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0),
                           (int(self.x), int(self.y)), self.radius)
