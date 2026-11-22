import math
from datetime import datetime

import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SIZES = [2, 5, 10]         
FONT_SIZES = [18, 28, 42]   

SHAPE_TOOLS = {"Line", "Rect", "Square", "Circle", "R-Tri", "Eq-Tri", "Rhombus"}


def shape_points(tool, start, end):
    x0, y0 = start
    x1, y1 = end
    if tool == "R-Tri":
        return [(x0, y0), (x0, y1), (x1, y1)]
    if tool == "Eq-Tri":
        base = x1 - x0
        h = abs(base) * math.sqrt(3) / 2
        apex_y = y1 - h if y0 <= y1 else y1 + h
        return [(x0, y1), (x1, y1), ((x0 + x1) / 2, apex_y)]
    if tool == "Rhombus":
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        return [(mx, y0), (x1, my), (mx, y1), (x0, my)]
    return []


def draw_shape(surf, tool, color, start, end, width):
    x0, y0 = start
    x1, y1 = end
    if tool == "Line":
        pygame.draw.line(surf, color, start, end, width)
        if width > 2:  # round caps so thick lines look clean
            pygame.draw.circle(surf, color, start, width // 2)
            pygame.draw.circle(surf, color, end, width // 2)
    elif tool == "Rect":
        rect = pygame.Rect(min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
        pygame.draw.rect(surf, color, rect, width)
    elif tool == "Square":
        side = min(abs(x1 - x0), abs(y1 - y0))
        sx = x0 if x1 >= x0 else x0 - side
        sy = y0 if y1 >= y0 else y0 - side
        pygame.draw.rect(surf, color, pygame.Rect(sx, sy, side, side), width)
    elif tool == "Circle":
        radius = int(math.hypot(x1 - x0, y1 - y0))
        if radius > 0:
            pygame.draw.circle(surf, color, start, radius, width)
    elif tool in ("R-Tri", "Eq-Tri", "Rhombus"):
        pygame.draw.polygon(surf, color, shape_points(tool, start, end), width)


def draw_stroke(surf, color, p0, p1, width):
    pygame.draw.line(surf, color, p0, p1, width)
    if width > 2:  # fill gaps at joints
        pygame.draw.circle(surf, color, p1, width // 2)


def flood_fill(surf, pos, new_color):
    w, h = surf.get_size()
    x, y = pos
    if not (0 <= x < w and 0 <= y < h):
        return
    target = surf.get_at((x, y))[:3]
    fill = tuple(new_color[:3])
    if target == fill:
        return

    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if surf.get_at((x, y))[:3] != target:
            continue
        xl = x
        while xl > 0 and surf.get_at((xl - 1, y))[:3] == target:
            xl -= 1
        xr = x
        while xr < w - 1 and surf.get_at((xr + 1, y))[:3] == target:
            xr += 1
        for i in range(xl, xr + 1):
            surf.set_at((i, y), fill)
        for ny in (y - 1, y + 1):
            if 0 <= ny < h:
                in_span = False
                for i in range(xl, xr + 1):
                    if surf.get_at((i, ny))[:3] == target:
                        if not in_span:
                            stack.append((i, ny))
                            in_span = True
                    else:
                        in_span = False


def save_canvas(surf):
    name = datetime.now().strftime("canvas_%Y%m%d_%H%M%S.png")
    pygame.image.save(surf, name)
    return name

