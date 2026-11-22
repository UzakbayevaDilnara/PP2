import pygame
import sys
from player import MusicPlayer

def main():
    pygame.init()
    screen = pygame.display.set_mode((700, 400))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()

    player = MusicPlayer("music")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_q:
                    running = False

        screen.fill((30, 30, 40))
        player.draw(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
