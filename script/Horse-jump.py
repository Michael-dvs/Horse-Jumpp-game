import pygame
import random
import sys

# Inisialisasi Pygame
pygame.init()

# Ukuran layar
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# konfigurasi warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY_ALPHA = (0, 0, 0, 150)  # Warna abu-abu dengan transparansi

# Membuat kelas untuk kuda
class Kuda(pygame.sprite.Sprite):
    def __init__(self, scale=1):
        super().__init__()
        self.images = [pygame.image.load('assets/kuda.png').convert_alpha(),
                       pygame.image.load('assets/kuda_lompat.png').convert_alpha()]  # Gambar kuda dan kuda loncat
        self.index = 0  # Indeks untuk gambar saat ini
        self.image = pygame.transform.scale(self.images[self.index], (int(80 * scale), int(80 * scale)))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (100, SCREEN_HEIGHT)  # Atur posisi awal kuda
        self.gravity = 0.8
        self.jump_power = -5
        self.jump = False

        # Buat mask dari gambar kuda
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if self.jump:
            self.rect.y += self.jump_power
            self.jump_power += self.gravity
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT
                self.jump = False
                self.index = 0  # Kembali ke gambar kuda saat di tanah
        self.image = pygame.transform.scale(self.images[self.index], (self.rect.width, self.rect.height))

    def jump_start(self):
        if not self.jump:
            self.jump = True
            self.jump_power = -14
            self.index = 1  # Ganti ke gambar kuda loncat

# Membuat kelas untuk rintangan
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed, scale=1):
        super().__init__()
        self.original_image = pygame.image.load('assets/kaktus.png').convert_alpha()  # Mengubah gambar menjadi kaktus.png
        self.image = pygame.transform.scale(self.original_image, (int(70 * scale), int(90 * scale)))  # Sesuaikan ukuran
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.speed = speed

        # Buat mask dari gambar obstacle
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right <= 2:
            self.kill()

# Membuat kelas untuk menghitung skor
class Score(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.high_score = 0
        self.load_high_score()
        self.font = pygame.font.Font(None, 36)
        self.image = None
        self.rect = None

    def update(self):
        self.score += 1
        self.render()

    def render(self):
        score_text = f"Score: {self.score}"
        self.image = self.font.render(score_text, True, BLACK)
        self.rect = self.image.get_rect()

    def display(self, screen):
        screen.blit(self.image, (10, 10))

    def load_high_score(self):
        try:
            with open("data/high_score.txt", "r") as file:
                self.high_score = int(file.read())
        except FileNotFoundError:
            self.high_score = 0

    def save_high_score(self):
        with open("data/high_score.txt", "w") as file:
            file.write(str(self.high_score))

# Fungsi untuk memulai permainan
def main():
    while True:
        game_loop()

def game_loop():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("KUDA LONCAT NGIHAAA!!!")

    # Menginisialisasi sprites
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    kuda_sprite = Kuda(scale=0.9)  # Atur skala gambar kuda di sini
    all_sprites.add(kuda_sprite)
    score = Score()
    all_sprites.add(score)

    # Mengatur background
    background = pygame.image.load('assets/background.jpg').convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_x = 0

    # Clock untuk mengatur kecepatan frame
    clock = pygame.time.Clock()

    obstacle_frequency = 2
    obstacle_speed = 5

    # Variable untuk kontrol pause
    paused = False
    game_over = False

    # Loop permainan
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not kuda_sprite.jump and not paused and not game_over:
                    kuda_sprite.jump_start()
                elif event.key == pygame.K_ESCAPE:  # Pause dengan tombol Esc
                    paused = not paused
                else:
                    if event.key == pygame.K_SPACE and game_over:
                        # Mulai ulang game dari awal
                        return

        if not paused and not game_over:
            # Menggerakkan latar belakang
            bg_x -= 1
            if bg_x <= -SCREEN_WIDTH:
                bg_x = 0

            # Membuat rintangan secara acak
            obstacle_frequency += 1
            if  obstacle_frequency == 60:
                obstacle_frequency = 0
                new_obstacle = Obstacle(obstacle_speed)
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)

            # Mempercepat permainan seiring dengan waktu
            if score.score % 500 == 0:
                obstacle_speed += 1

            # Update dan render sprites
            screen.blit(background, (bg_x, 0))
            screen.blit(background, (bg_x + SCREEN_WIDTH, 0))
            all_sprites.update()
            all_sprites.draw(screen)

            # Memeriksa tabrakan dengan mask
            for obstacle in obstacles:
                if pygame.sprite.collide_mask(kuda_sprite, obstacle):
                    game_over = True
                    if score.score > score.high_score:
                        score.high_score = score.score
                        score.save_high_score()
                    break

        elif paused:
            # Ketika game dalam mode pause
            screen.fill(GRAY_ALPHA)  # Latar belakang menjadi gelap

            # Tampilkan pesan "Game Paused"
            font = pygame.font.Font(None, 48)
            paused_text = font.render("Game Paused", True, WHITE)
            paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(paused_text, paused_rect)

        elif game_over:
            # Ketika game over
            failed_background = pygame.image.load('assets/fail_background.jpg').convert()
            failed_background = pygame.transform.scale(failed_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(failed_background, (0, 0))

            # Tampilkan pesan "Game Over"
            font = pygame.font.Font(None, 48)
            game_over_text = font.render("Game Over", True, WHITE)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, game_over_rect)

            # Tampilkan skor
            score_text = f"Your Score: {score.score}"
            score_text2 = f"High Score: {score.high_score}"
            score_font = pygame.font.Font(None, 36)
            score_render = score_font.render(score_text, True, WHITE)
            score_rect = score_render.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            score_render2 = score_font.render(score_text2, True, WHITE)
            score_rect2 = score_render2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            screen.blit(score_render, score_rect)
            screen.blit(score_render2, score_rect2)

        # Memperbarui layar
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
