import os
from datetime import datetime

import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HAND_PATH = os.path.join(BASE_DIR, "images", "mickey_hand.png")


def make_placeholder_hand(path):
    w, h = 110, 290
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    O = 4 

    parts = [
        ("rrect", pygame.Rect(cx - 10, 8, 20, 150), 10),      
        ("ellipse", pygame.Rect(cx - 34, 120, 68, 90), 0),    
        ("ellipse", pygame.Rect(cx - 56, 135, 34, 54), 0),    
        ("circle", pygame.Rect(cx + 14, 112, 26, 26), 0),    
        ("circle", pygame.Rect(cx + 20, 134, 26, 26), 0),
        ("circle", pygame.Rect(cx + 20, 156, 24, 24), 0),
        ("rrect", pygame.Rect(cx - 28, 200, 56, 34), 10),     
    ]

    def draw_part(color, kind, rect, radius, inflate):
        r = rect.inflate(inflate * 2, inflate * 2)
        if kind == "rrect":
            pygame.draw.rect(surf, color, r, border_radius=radius + inflate)
        else:
            pygame.draw.ellipse(surf, color, r)

  
    sleeve = pygame.Rect(cx - 16, 228, 32, h - 228)
    pygame.draw.rect(surf, (0, 0, 0), sleeve.inflate(O * 2, O * 2))
    for kind, rect, radius in parts:
        draw_part((0, 0, 0), kind, rect, radius, O)     
    pygame.draw.rect(surf, (210, 20, 20), sleeve)
    for kind, rect, radius in parts:
        draw_part((255, 255, 255), kind, rect, radius, 0)  

    pygame.draw.line(surf, (0, 0, 0), (cx - 22, 212), (cx + 22, 212), 2)
    pygame.draw.line(surf, (0, 0, 0), (cx - 24, 222), (cx + 24, 222), 2)
    for y in (126, 148):
        pygame.draw.arc(surf, (0, 0, 0), (cx + 12, y, 22, 20), 4.2, 6.0, 2)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    pygame.image.save(surf, path)


def _pad_to_pivot(img):
   
    w, h = img.get_size()
    padded = pygame.Surface((w, h * 2), pygame.SRCALPHA)
    padded.blit(img, (0, 0))
    return padded


class MickeyClock:
    def __init__(self, center):
        if not os.path.exists(HAND_PATH):
            make_placeholder_hand(HAND_PATH)
        hand = pygame.image.load(HAND_PATH).convert_alpha()
        self.center = pygame.math.Vector2(center)
        self.right_hand = _pad_to_pivot(hand)                                      
        self.left_hand = _pad_to_pivot(pygame.transform.flip(hand, True, False))   
        self.minutes = 0
        self.seconds = 0

    def update(self):
        now = datetime.now()
        self.minutes = now.minute
        self.seconds = min(now.second, 59)   

    @staticmethod
    def _angle(value):
        return -value * 6

    def _blit_rotated(self, screen, image, angle):
        rotated = pygame.transform.rotate(image, angle)
        rect = rotated.get_rect(center=(round(self.center.x), round(self.center.y)))
        screen.blit(rotated, rect)

    def draw(self, screen):
        c = (round(self.center.x), round(self.center.y))
        pygame.draw.circle(screen, (255, 255, 255), c, 300)
        pygame.draw.circle(screen, (0, 0, 0), c, 300, 4)
        for i in range(60):
            v = pygame.math.Vector2(0, -1).rotate(i * 6)
            length = 20 if i % 5 == 0 else 8
            p1 = self.center + v * (296 - length)
            p2 = self.center + v * 294
            pygame.draw.line(screen, (0, 0, 0), p1, p2, 3 if i % 5 == 0 else 1)

        self._blit_rotated(screen, self.right_hand, self._angle(self.minutes))
        self._blit_rotated(screen, self.left_hand, self._angle(self.seconds))
        pygame.draw.circle(screen, (0, 0, 0), c, 8)
