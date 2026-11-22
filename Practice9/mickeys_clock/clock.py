import pygame
import math
import datetime
import os

class MickeyClock:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.hand_length = 150
        self.hand_image = None
        self.minute_angle = 0
        self.second_angle = 0

        path = os.path.join(os.path.dirname(__file__), "images", "mickey_hand.png")
        if os.path.exists(path):
            self.hand_image = pygame.image.load(path).convert_alpha()
            self.hand_image = pygame.transform.scale(
                self.hand_image, (self.hand_length, 30)
            )

    def _draw_hand(self, surface, angle_deg, color, length, width):
        angle_rad = math.radians(angle_deg - 90)
        end_x = self.cx + length * math.cos(angle_rad)
        end_y = self.cy + length * math.sin(angle_rad)
        pygame.draw.line(surface, color, (self.cx, self.cy), (end_x, end_y), width)
        pygame.draw.circle(surface, color, (int(end_x), int(end_y)), width // 2)

    def update(self):
        now = datetime.datetime.now()
        self.minute_angle = (now.minute + now.second / 60.0) * 6
        self.second_angle = now.second * 6

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 220, 0), (self.cx, self.cy), 250)
        pygame.draw.circle(surface, (0, 0, 0), (self.cx, self.cy), 250, 4)

        font = pygame.font.SysFont("Arial", 40, bold=True)
        for num, ang in [(12, -90), (3, 0), (6, 90), (9, 180)]:
            rad = math.radians(ang)
            x = self.cx + 200 * math.cos(rad)
            y = self.cy + 200 * math.sin(rad)
            text = font.render(str(num), True, (0, 0, 0))
            rect = text.get_rect(center=(x, y))
            surface.blit(text, rect)

        self._draw_hand(surface, self.minute_angle, (200, 0, 0), 150, 10)
        self._draw_hand(surface, self.second_angle, (0, 0, 200), 110, 6)

        pygame.draw.circle(surface, (0, 0, 0), (self.cx, self.cy), 12)
