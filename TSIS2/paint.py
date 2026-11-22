import sys

import pygame

from tools import (BLACK, FONT_SIZES, SHAPE_TOOLS, SIZES, WHITE, draw_shape,
                   draw_stroke, flood_fill, save_canvas)

pygame.init()

WIDTH, HEIGHT = 1000, 720
TOOLBAR_H = 104
CANVAS_W, CANVAS_H = WIDTH, HEIGHT - TOOLBAR_H
FPS = 60

GRAY = (225, 225, 225)
DARK = (70, 70, 70)
HILITE = (120, 180, 255)

PALETTE = [
    (0, 0, 0), (255, 255, 255), (128, 128, 128), (200, 0, 0),
    (255, 120, 0), (255, 220, 0), (0, 170, 0), (0, 200, 200),
    (0, 90, 220), (120, 0, 200), (230, 80, 160), (130, 80, 30),
]

TOOLS = [
    ("Pencil", pygame.K_p), ("Line", pygame.K_l), ("Rect", pygame.K_r),
    ("Square", pygame.K_s), ("Circle", pygame.K_c), ("R-Tri", pygame.K_t),
    ("Eq-Tri", pygame.K_e), ("Rhombus", pygame.K_h), ("Eraser", pygame.K_x),
    ("Fill", pygame.K_f), ("Text", pygame.K_k), ("Picker", pygame.K_i),
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint - TSIS 2")
clock = pygame.time.Clock()
ui_font = pygame.font.SysFont("arial", 15)
small_font = pygame.font.SysFont("arial", 13)

BTN_W, BTN_H, BTN_GAP = 78, 32, 4
tool_rects = [
    pygame.Rect(6 + i * (BTN_W + BTN_GAP), 6, BTN_W, BTN_H)
    for i in range(len(TOOLS))
]
SWATCH = 30
palette_rects = [
    pygame.Rect(6 + i * (SWATCH + 4), 46, SWATCH, SWATCH)
    for i in range(len(PALETTE))
]
size_rects = [pygame.Rect(520 + i * 46, 44, 40, 34) for i in range(3)]
cur_color_rect = pygame.Rect(720, 44, 34, 34)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)
history = []  # for Ctrl+Z

tool = "Pencil"
color = BLACK
size_idx = 1
dragging = False
start_pos = None
last_pos = None

text_active = False
text_pos = (0, 0)
text_buf = ""

status = "Ready. Ctrl+S saves, Ctrl+Z undoes."
status_time = pygame.time.get_ticks()


def set_status(msg):
    global status, status_time
    status, status_time = msg, pygame.time.get_ticks()


def push_history():
    history.append(canvas.copy())
    if len(history) > 20:
        history.pop(0)


def to_canvas(pos):
    return pos[0], pos[1] - TOOLBAR_H


def in_canvas(pos):
    return pos[1] >= TOOLBAR_H


def commit_text():
    global text_active, text_buf
    if text_buf:
        push_history()
        font = pygame.font.SysFont("arial", FONT_SIZES[size_idx])
        canvas.blit(font.render(text_buf, True, color), text_pos)
    text_active, text_buf = False, ""


def cancel_text():
    global text_active, text_buf
    text_active, text_buf = False, ""


def handle_toolbar_click(pos):
    global tool, color, size_idx
    if text_active:
        commit_text()
    for r, (name, _) in zip(tool_rects, TOOLS):
        if r.collidepoint(pos):
            tool = name
            return
    for r, c in zip(palette_rects, PALETTE):
        if r.collidepoint(pos):
            color = c
            return
    for i, r in enumerate(size_rects):
        if r.collidepoint(pos):
            size_idx = i
            return


def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_H))
    pygame.draw.line(screen, DARK, (0, TOOLBAR_H - 1), (WIDTH, TOOLBAR_H - 1))

    for r, (name, key) in zip(tool_rects, TOOLS):
        active = name == tool
        pygame.draw.rect(screen, HILITE if active else WHITE, r, border_radius=4)
        pygame.draw.rect(screen, DARK, r, 2 if active else 1, border_radius=4)
        label = ui_font.render(name, True, BLACK)
        screen.blit(label, label.get_rect(center=(r.centerx, r.centery - 4)))
        hint = small_font.render(pygame.key.name(key).upper(), True, DARK)
        screen.blit(hint, hint.get_rect(center=(r.centerx, r.bottom - 7)))

    for r, c in zip(palette_rects, PALETTE):
        pygame.draw.rect(screen, c, r)
        pygame.draw.rect(screen, HILITE if c == color else DARK, r,
                         3 if c == color else 1)

    for i, r in enumerate(size_rects):
        active = i == size_idx
        pygame.draw.rect(screen, HILITE if active else WHITE, r, border_radius=4)
        pygame.draw.rect(screen, DARK, r, 2 if active else 1, border_radius=4)
        pygame.draw.circle(screen, BLACK, r.center, SIZES[i] // 2 + 1)
        n = small_font.render(str(i + 1), True, DARK)
        screen.blit(n, (r.x + 3, r.y + 1))

    screen.blit(ui_font.render("Size:", True, BLACK), (470, 52))
    screen.blit(ui_font.render("Color:", True, BLACK), (668, 52))
    pygame.draw.rect(screen, color, cur_color_rect)
    pygame.draw.rect(screen, BLACK, cur_color_rect, 2)

    msg = status if pygame.time.get_ticks() - status_time < 4000 else (
        f"Tool: {tool}   Size: {SIZES[size_idx]} px   "
        "[1/2/3] size  [Ctrl+S] save  [Ctrl+Z] undo")
    screen.blit(ui_font.render(msg, True, BLACK), (8, 84))


def render():
    screen.fill(WHITE)
    view = canvas

    if dragging and tool in SHAPE_TOOLS and start_pos and last_pos:
        view = canvas.copy()
        draw_shape(view, tool, color, start_pos, last_pos, SIZES[size_idx])

    if text_active:
        view = view.copy() if view is canvas else view
        font = pygame.font.SysFont("arial", FONT_SIZES[size_idx])
        shown = font.render(text_buf, True, color)
        view.blit(shown, text_pos)
        if (pygame.time.get_ticks() // 500) % 2 == 0:  # blinking caret
            cx = text_pos[0] + shown.get_width() + 1
            pygame.draw.line(view, color, (cx, text_pos[1]),
                             (cx, text_pos[1] + font.get_height()), 2)

    screen.blit(view, (0, TOOLBAR_H))
    draw_toolbar()
    pygame.display.flip()


def main():
    global tool, color, size_idx, dragging, start_pos, last_pos
    global text_active, text_pos, text_buf

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                ctrl = event.mod & pygame.KMOD_CTRL

                if ctrl and event.key == pygame.K_s:
                    if text_active:
                        commit_text()
                    set_status("Saved: " + save_canvas(canvas))
                    continue
                if ctrl and event.key == pygame.K_z:
                    if history:
                        cancel_text()
                        canvas.blit(history.pop(), (0, 0))
                    continue

                if text_active:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        commit_text()
                    elif event.key == pygame.K_ESCAPE:
                        cancel_text()
                    elif event.key == pygame.K_BACKSPACE:
                        text_buf = text_buf[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        text_buf += event.unicode
                    continue

                if event.key == pygame.K_1:
                    size_idx = 0
                elif event.key == pygame.K_2:
                    size_idx = 1
                elif event.key == pygame.K_3:
                    size_idx = 2
                elif event.key == pygame.K_ESCAPE:
                    dragging = False
                else:
                    for name, key in TOOLS:
                        if event.key == key:
                            tool = name

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not in_canvas(event.pos):
                    handle_toolbar_click(event.pos)
                    continue
                cpos = to_canvas(event.pos)

                if tool == "Text":
                    if text_active:
                        commit_text()
                    text_active = True
                    text_pos = cpos
                    text_buf = ""
                elif tool == "Fill":
                    push_history()
                    flood_fill(canvas, cpos, color)
                elif tool == "Picker":
                    color = tuple(canvas.get_at(cpos)[:3])
                elif tool in ("Pencil", "Eraser"):
                    push_history()
                    dragging = True
                    last_pos = cpos
                    col = WHITE if tool == "Eraser" else color
                    w = SIZES[size_idx] * (3 if tool == "Eraser" else 1)
                    pygame.draw.circle(canvas, col, cpos, max(1, w // 2))
                else: 
                    dragging = True
                    start_pos = cpos
                    last_pos = cpos

            elif event.type == pygame.MOUSEMOTION and dragging:
                cpos = to_canvas(event.pos)
                cpos = (max(0, min(CANVAS_W - 1, cpos[0])),
                        max(0, min(CANVAS_H - 1, cpos[1])))
                if tool in ("Pencil", "Eraser"):
                    col = WHITE if tool == "Eraser" else color
                    w = SIZES[size_idx] * (3 if tool == "Eraser" else 1)
                    draw_stroke(canvas, col, last_pos, cpos, w)
                last_pos = cpos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging and tool in SHAPE_TOOLS and start_pos:
                    push_history()
                    draw_shape(canvas, tool, color, start_pos,
                               to_canvas(event.pos), SIZES[size_idx])
                dragging = False
                start_pos = None

        render()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

