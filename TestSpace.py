import pygame
import sys
from Snake.RLBrainySnake import *

window = pygame.display.set_mode((500, 500))
pygame.display.set_caption("wow_snake")
fps = pygame.time.Clock()
score = 0

w, h = pygame.display.get_surface().get_size()
snake = BrainSnake(0, width=w, height=h)


def segment_over():
    pass


def gameOver():
    print('game over')
    pygame.quit()
    sys.exit()

tickspeed  = 10

while True:
    if snake.move() == 1:
        score += 1
        print('score:  ', score)

    window.fill(pygame.Color(255, 255, 255))
    for pos in snake.get_body():
        pygame.draw.rect(window, pygame.Color(0, 200, 0), pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(snake.foodLoc[0], snake.foodLoc[1], 10, 10))
    if snake.is_alive == False:
        segment_over()
        snake.reset()
        score = 0

    pygame.display.set_caption(str(score) + 'wow snake | score: ' + str(score))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameOver()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                tickspeed += 10
                print(tickspeed)
            if event.key == pygame.K_LEFT:
                tickspeed -= 100
                print(tickspeed)
    fps.tick(tickspeed)  # speed of the game
