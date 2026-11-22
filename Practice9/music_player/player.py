import pygame
import os

class MusicPlayer:
    def __init__(self, music_dir):
        pygame.mixer.init()
        self.music_dir = music_dir
        self.tracks = []
        self.current = 0
        self.playing = False
        self._load_tracks()

    def _load_tracks(self):
        if os.path.isdir(self.music_dir):
            for f in sorted(os.listdir(self.music_dir)):
                if f.lower().endswith((".mp3", ".wav", ".ogg")):
                    self.tracks.append(os.path.join(self.music_dir, f))

    def play(self):
        if not self.tracks or self.playing:
            return
        try:
            pygame.mixer.music.load(self.tracks[self.current])
            pygame.mixer.music.play()
            self.playing = True
        except pygame.error:
            pass

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def next_track(self):
        if not self.tracks:
            return
        was_playing = self.playing
        pygame.mixer.music.stop()
        self.current = (self.current + 1) % len(self.tracks)
        self.playing = False
        if was_playing:
            self.play()

    def prev_track(self):
        if not self.tracks:
            return
        was_playing = self.playing
        pygame.mixer.music.stop()
        self.current = (self.current - 1) % len(self.tracks)
        self.playing = False
        if was_playing:
            self.play()

    def draw(self, surface):
        font_big = pygame.font.SysFont("Arial", 36, bold=True)
        font = pygame.font.SysFont("Arial", 24)

        title = font_big.render("Music Player", True, (255, 255, 255))
        surface.blit(title, (30, 30))

        if self.tracks:
            name = os.path.basename(self.tracks[self.current])
            info = f"Track {self.current + 1}/{len(self.tracks)}: {name}"
        else:
            info = "No tracks found (music/ folder empty)"
        surface.blit(font.render(info, True, (200, 200, 200)), (30, 110))

        status = "PLAYING" if self.playing else "STOPPED"
        color = (0, 255, 0) if self.playing else (255, 80, 80)
        surface.blit(font.render(f"Status: {status}", True, color), (30, 160))

        if self.playing and pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() / 1000.0
            bar_x, bar_y, bar_w, bar_h = 30, 220, 640, 20
            pygame.draw.rect(surface, (60, 60, 80), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, (0, 200, 255), (bar_x, bar_y, bar_w, bar_h))
            surface.blit(font.render(f"{pos:.1f}s", True, (255, 255, 255)),
                         (bar_x, bar_y + 30))

        controls = "P=Play  S=Stop  N=Next  B=Back  Q=Quit"
        surface.blit(font.render(controls, True, (180, 180, 255)), (30, 320))
