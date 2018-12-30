import pygame
import sys
from Snake.RLBrainySnake import *

window = pygame.display.set_mode((300, 300))
pygame.display.set_caption("wow_snake")
fps = pygame.time.Clock()
score = 0

w, h = pygame.display.get_surface().get_size()
snake = BrainSnake(0, width=w, height=h)


def gameOver():
    print('game over')
    pygame.quit()
    sys.exit()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameOver()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                snake.set_direction('RIGHT')
            if event.key == pygame.K_UP:
                snake.set_direction('UP')
            if event.key == pygame.K_DOWN:
                snake.set_direction('DOWN')
            if event.key == pygame.K_LEFT:
                snake.set_direction('LEFT')
    if snake.move() == 1:
        score += 1
        print('score:  ', score)
    # print(snake.global_fitness, snake.rewards)

    window.fill(pygame.Color(255, 255, 255))
    for pos in snake.get_body():
        pygame.draw.rect(window, pygame.Color(0, 200, 0), pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(snake.foodLoc[0], snake.foodLoc[1], 10, 10))
    if snake.is_alive == False:
        gameOver()
    pygame.display.set_caption('wow snake | score: ' + str(score))
    pygame.display.flip()
    fps.tick(1)  # speed of the game
