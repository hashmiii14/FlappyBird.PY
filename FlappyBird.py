import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 600
GRAVITY = 0.5
FLAP_STRENGTH = -10
PIPE_GAP = 200  # Increased gap for easier gameplay
PIPE_WIDTH = 70
INITIAL_PIPE_SPEED = 4
SPEED_INCREMENT = 0.5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Load assets
bird_img = pygame.image.load("C:\\Users\\MD HASHMI\\OneDrive\\Desktop\\Coding\\Python\\cheel.jpg")
bird_img = pygame.transform.scale(bird_img, (40, 40))
background_img = pygame.image.load("C:\\Users\\MD HASHMI\\OneDrive\\Desktop\\Coding\\Python\\background.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
photo_img = pygame.image.load("C:\\Users\\MD HASHMI\\OneDrive\\Desktop\\Coding\\Python\\hashmi.jpg")
photo_img = pygame.transform.scale(photo_img, (200, 200))

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Bird
bird = pygame.Rect(100, HEIGHT // 2, 40, 40)
velocity = 0

# Pipes
pipes = []
def spawn_pipe():
    height = random.randint(150, 300)
    pipes.append(pygame.Rect(WIDTH, height, PIPE_WIDTH, HEIGHT - height))
    pipes.append(pygame.Rect(WIDTH, 0, PIPE_WIDTH, height - PIPE_GAP))

spawn_pipe()
score = 0
high_score = 0
pipe_speed = INITIAL_PIPE_SPEED
running = True
started = False

# Game over flag
game_over = False

def reset_game():
    global bird, velocity, pipes, score, pipe_speed, started, game_over
    bird.y = HEIGHT // 2
    velocity = 0
    pipes.clear()
    spawn_pipe()
    score = 0
    pipe_speed = INITIAL_PIPE_SPEED
    started = True
    game_over = False

# Game loop
while running:
    screen.blit(background_img, (0, 0))
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if game_over:
                reset_game()
            elif not started:
                started = True
                reset_game()
            velocity = FLAP_STRENGTH
    
    if started and not game_over:
        # Increase speed with score
        pipe_speed = INITIAL_PIPE_SPEED + (score * SPEED_INCREMENT)
        
        # Bird mechanics
        velocity += GRAVITY
        bird.y += velocity
        screen.blit(bird_img, (bird.x, bird.y))
        
        # Pipe movement
        for pipe in pipes:
            pipe.x -= int(pipe_speed)
            pygame.draw.rect(screen, GREEN, pipe)
        
        # Pipe collision & Respawn
        if pipes[0].x < -PIPE_WIDTH:
            pipes = pipes[2:]
            spawn_pipe()
            score += 1
            high_score = max(high_score, score)
        
        # Collision detection
        for pipe in pipes:
            if bird.colliderect(pipe):
                game_over = True
                started = False
        
        # Ground collision
        if bird.y > HEIGHT or bird.y < 0:
            game_over = True
            started = False
    
    if game_over:
        screen.blit(photo_img, (WIDTH//2 - 100, HEIGHT//2 - 250))
        font = pygame.font.Font(None, 50)
        game_over_text = font.render("Game Over", True, BLACK)
        restart_text = pygame.font.Font(None, 36).render("Press SPACE to Restart", True, BLACK)
        score_text = pygame.font.Font(None, 36).render(f"Your Score: {score}", True, BLACK)
        high_score_text = pygame.font.Font(None, 36).render(f"High Score: {high_score}", True, BLACK)
        screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 20))
        screen.blit(score_text, (WIDTH//2 - 80, HEIGHT//2 + 60))
        screen.blit(high_score_text, (WIDTH//2 - 80, HEIGHT//2 + 90))
    elif not started:
        # Show start message and user's photo
        screen.blit(photo_img, (WIDTH//2 - 100, HEIGHT//2 - 150))
        font = pygame.font.Font(None, 36)
        text = font.render("Press SPACE to Start", True, BLACK)
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 + 100))
    
    # Score display
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()

