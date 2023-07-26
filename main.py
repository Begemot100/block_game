import pygame
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
BALL_RADIUS = 10
BRICK_ROWS, BRICK_COLS = 3, 10
LIVES_FONT = pygame.font.SysFont("comicsans", 40)

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")


class Paddle:
    VEL = 5

    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self, direction=1):
        self.rect.x += self.VEL * direction


class Ball:
    VEL = 5

    def __init__(self, x, y, radius, color):
        self.rect = pygame.Rect(x - radius, y - radius, 2 * radius, 2 * radius)
        self.color = color
        self.x_vel = 0
        self.y_vel = -self.VEL

    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def set_vel(self, x_vel, y_vel):
        self.x_vel = x_vel
        self.y_vel = y_vel

    def draw(self):
        pygame.draw.circle(win, self.color, self.rect.center, BALL_RADIUS)


class Brick:
    def __init__(self, x, y, width, height, health, colors):
        self.rect = pygame.Rect(x, y, width, height)
        self.health = health
        self.max_health = health
        self.colors = colors

    def draw(self):
        pygame.draw.rect(win, self.interpolate_color(), self.rect)

    def collide(self, ball):
        if not self.rect.colliderect(ball.rect):
            return False

        self.hit()
        ball.set_vel(ball.x_vel, -ball.y_vel)
        return True

    def hit(self):
        self.health -= 1

    def interpolate_color(self):
        t = self.health / self.max_health
        return tuple(int(a + (b - a) * t) for a, b in zip(self.colors[0], self.colors[1]))


def draw(paddle, ball, bricks, lives):
    win.fill("white")
    paddle.draw()
    ball.draw()

    for brick in bricks:
        brick.draw()

    lives_text = LIVES_FONT.render(f"Lives: {lives}", 1, "black")
    win.blit(lives_text, (10, HEIGHT - lives_text.get_height() - 10))

    pygame.display.update()


def ball_collision(ball):
    if ball.rect.left <= 0 or ball.rect.right >= WIDTH:
        ball.set_vel(-ball.x_vel, ball.y_vel)
    if ball.rect.bottom >= HEIGHT or ball.rect.top <= 0:
        ball.set_vel(ball.x_vel, -ball.y_vel)


def ball_paddle_collision(ball, paddle):
    if not ball.rect.colliderect(paddle.rect):
        return

    paddle_center = paddle.rect.centerx
    distance_to_center = ball.rect.centerx - paddle_center

    percent_width = distance_to_center / paddle.rect.width
    angle = percent_width * 90
    angle_radians = math.radians(angle)

    x_vel = math.sin(angle_radians) * ball.VEL
    y_vel = -math.cos(angle_radians) * ball.VEL

    ball.set_vel(x_vel, y_vel)


def generate_bricks(rows, cols):
    gap = 2
    brick_width = WIDTH // cols - gap
    brick_height = 20

    bricks = []
    for row in range(rows):
        for col in range(cols):
            brick_x = col * (brick_width + gap)
            brick_y = row * (brick_height + gap)
            brick = Brick(brick_x, brick_y, brick_width, brick_height, 2, [GREEN, RED])
            bricks.append(brick)

    return bricks


def main():
    clock = pygame.time.Clock()

    paddle_x = WIDTH/2 - PADDLE_WIDTH/2
    paddle_y = HEIGHT - PADDLE_HEIGHT - 5
    paddle = Paddle(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT, BLACK)
    ball = Ball(WIDTH/2, paddle_y - BALL_RADIUS, BALL_RADIUS, BLACK)

    bricks = generate_bricks(BRICK_ROWS, BRICK_COLS)
    lives = 3

    def reset():
        paddle.rect.x = paddle_x
        paddle.rect.y = paddle_y
        ball.rect.x = WIDTH/2 - BALL_RADIUS
        ball.rect.y = paddle_y - BALL_RADIUS

    def display_text(text):
        text_render = LIVES_FONT.render(text, 1, "red")
        win.blit(text_render, (WIDTH/2 - text_render.get_width() / 2, HEIGHT/2 - text_render.get_height() / 2))
        pygame.display.update()
        pygame.time.delay(3000)

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and paddle.rect.left >= 0:
            paddle.move(-1)
        if keys[pygame.K_RIGHT] and paddle.rect.right <= WIDTH:
            paddle.move(1)

        ball.move()
        ball_collision(ball)
        ball_paddle_collision(ball, paddle)

        for brick in bricks[:]:
            if brick.collide(ball):
                if brick.health <= 0:
                    bricks.remove(brick)

        # Lives check
        if ball.rect.bottom >= HEIGHT:
            lives -= 1
            ball.rect.x = paddle.rect.centerx - BALL_RADIUS
            ball.rect.y = paddle.rect.top - BALL_RADIUS
            ball.set_vel(0, ball.VEL)

        if lives <= 0:
            bricks = generate_bricks(BRICK_ROWS, BRICK_COLS)
            lives = 3
            reset()
            display_text("You Lost!")

        if len(bricks) == 0:
            bricks = generate_bricks(BRICK_ROWS, BRICK_COLS)
            lives = 3
            reset()
            display_text("You Won!")

        draw(paddle, ball, bricks, lives)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()

