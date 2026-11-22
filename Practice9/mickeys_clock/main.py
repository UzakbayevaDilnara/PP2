import pygame

from clock import MickeyClock

SIZE = 640


def main():
    pygame.init()
    screen = pygame.display.set_mode((SIZE, SIZE))
    pygame.display.set_caption("Mickey's Clock")
    font = pygame.font.SysFont("arial", 32, bold=True)
    clock = pygame.time.Clock()

    mickey = MickeyClock((SIZE // 2, SIZE // 2))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        mickey.update()   
        screen.fill((240, 240, 240))
        mickey.draw(screen)
        text = font.render(f"{mickey.minutes:02d}:{mickey.seconds:02d}", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=(SIZE // 2, SIZE - 25)))
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
