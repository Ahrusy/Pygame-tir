import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Duck Hunt - Improved Version")

# Цвета (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Загрузка фонового изображения (при наличии)
try:
    background = pygame.image.load('background.png').convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except Exception as e:
    print("Фоновое изображение не найдено. Используется заливка цветом.")
    background = None

# Загрузка звуковых эффектов (при наличии)
try:
    shot_sound = pygame.mixer.Sound('shot.wav')
except Exception as e:
    print("Звук выстрела не найден.")
    shot_sound = None

try:
    hit_sound = pygame.mixer.Sound('hit.wav')
except Exception as e:
    print("Звук попадания не найден.")
    hit_sound = None

# Параметры утки
DUCK_WIDTH, DUCK_HEIGHT = 60, 40
DUCK_SPEED_MIN = 3
DUCK_SPEED_MAX = 8

# Класс анимированной утки с поддержкой нескольких кадров
class AnimatedDuck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = []
        # Пытаемся загрузить кадры утки (duck1.png, duck2.png, ...)
        for i in range(1, 3):
            try:
                image = pygame.image.load(f'duck{i}.png').convert_alpha()
                image = pygame.transform.scale(image, (DUCK_WIDTH, DUCK_HEIGHT))
                self.frames.append(image)
            except Exception as e:
                pass

        # Если изображения не найдены, создаем простой прямоугольник
        if not self.frames:
            default_image = pygame.Surface((DUCK_WIDTH, DUCK_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(default_image, GREEN, default_image.get_rect())
            self.frames.append(default_image)

        self.current_frame = 0
        self.animation_time = 200  # время между сменой кадров в миллисекундах
        self.last_update = pygame.time.get_ticks()

        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        # Утка появляется с левой стороны экрана на случайной высоте
        self.rect.x = -DUCK_WIDTH
        self.rect.y = random.randint(50, HEIGHT - 100)
        # Задаем случайную скорость для утки
        self.speed = random.randint(DUCK_SPEED_MIN, DUCK_SPEED_MAX)

    def update(self):
        # Анимация: смена кадров
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_time:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        # Движение утки вправо
        self.rect.x += self.speed
        # Если утка вышла за правую границу, сбрасываем её позицию
        if self.rect.x > WIDTH:
            self.reset_position()

# Начальное количество уток
NUM_DUCKS = 3

# Группа спрайтов уток
ducks = pygame.sprite.Group()
for _ in range(NUM_DUCKS):
    duck = AnimatedDuck()
    ducks.add(duck)

# Шрифт для отображения счета и уровня
font = pygame.font.SysFont(None, 36)

# Параметры прицела
crosshair_radius = 15

def main():
    clock = pygame.time.Clock()
    score = 0  # Начальный счет
    level = 1  # Начальный уровень
    running = True

    # Скрываем стандартный курсор
    pygame.mouse.set_visible(False)

    while running:
        clock.tick(60)  # 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Обработка выстрела (нажатие кнопки мыши)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if shot_sound:
                    shot_sound.play()
                mouse_pos = pygame.mouse.get_pos()
                # Проверка попадания по каждой утке
                hit_ducks = [duck for duck in ducks if duck.rect.collidepoint(mouse_pos)]
                if hit_ducks:
                    for duck in hit_ducks:
                        duck.reset_position()
                    score += len(hit_ducks)
                    if hit_sound:
                        hit_sound.play()
                    print(f"Попадание! Счёт: {score}")

        # Обновление состояния уток
        ducks.update()

        # Пример повышения сложности: при каждых 10 очках добавляем новую утку (максимум 10 уток)
        if score >= level * 10 and len(ducks) < 10:
            level += 1
            new_duck = AnimatedDuck()
            ducks.add(new_duck)
            print(f"Уровень повышен! Уровень: {level}")

        # Отрисовка фона
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(WHITE)

        # Отрисовка уток
        ducks.draw(screen)

        # Отрисовка счета и уровня
        score_text = font.render(f"Счёт: {score}  Уровень: {level}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Отрисовка прицела (крестика)
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.circle(screen, RED, mouse_pos, crosshair_radius, 2)
        pygame.draw.line(screen, RED, (mouse_pos[0] - crosshair_radius, mouse_pos[1]),
                         (mouse_pos[0] + crosshair_radius, mouse_pos[1]), 2)
        pygame.draw.line(screen, RED, (mouse_pos[0], mouse_pos[1] - crosshair_radius),
                         (mouse_pos[0], mouse_pos[1] + crosshair_radius), 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()