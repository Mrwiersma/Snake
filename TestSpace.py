import pygame
import sys
from Snake.BrainySnake import *

window = pygame.display.set_mode((500, 500))
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
                snake.change_dir_to('RIGHT')
            if event.key == pygame.K_UP:
                snake.change_dir_to('UP')
            if event.key == pygame.K_DOWN:
                snake.change_dir_to('DOWN')
            if event.key == pygame.K_LEFT:
                snake.change_dir_to('LEFT')
    if snake.move() == 1:
        score += 1
        print('score:  ', score)
    print(snake.brain_input)
    snake.update_brain_input()
    #print(snake.global_fitness, snake.local_fitness)
    snake.update_fitness()

    window.fill(pygame.Color(255, 255, 255))
    for pos in snake.get_body():
        pygame.draw.rect(window, pygame.Color(0, 200, 0), pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(snake.foodLoc[0], snake.foodLoc[1], 10, 10))
    if snake.check_collision() == 1:
        gameOver()
    pygame.display.set_caption('wow snake | score: ' + str(score))
    pygame.display.flip()
    fps.tick(2)  #speed of the game
