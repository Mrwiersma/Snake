import pygame
import sys
from NeuralNet.NaturalSelectionV2 import *
from Snake.BrainySnakeV2 import *

network_dict = {0: {'mode': "Linear", "input": 11, "output": 16, "bias": True, "activation": "Sigmoid", "activation_params": []},
                1: {'mode': "Linear", "input": -1, "output": 2, "bias": True, "activation": "Sigmoid",
                    "activation_params": [0, 1, False]}}

window = pygame.display.set_mode((100, 100))

pygame.display.set_caption("wow_snake")
fps = pygame.time.Clock()

current_gen = 0
number_of_generation = 80

w, h = pygame.display.get_surface().get_size()
naturalSelector = NaturalSelection(BrainSnake, w, h)
naturalSelector.set_nn_layout(network_dict)
naturalSelector.generate_first_population(3000)


def generation_over(gen, highscore):
    print('All snakes of generation {} are dead.'.format(gen))
    print("Best fitness score of generation {}: {}".format(gen, highscore))
    print('Making new snakes')


def game_over():
    print('game over')
    pygame.quit()
    sys.exit()


def get_game_inputs(cur_tick):
    tick = cur_tick
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEDOWN:
                tick -= 1000
                print(tick)
            if event.key == pygame.K_PAGEUP:
                tick += 1000
                print(tick)
            if event.key == pygame.K_UP:
                tick += 10
                print(tick)
            if event.key == pygame.K_DOWN:
                tick -= 10
                print(tick)
        if tick < 10:
            tick = 10
    return tick


def show_snake_():
    pass


def show_snake_vision():
    pass


def show_info():
    pass


def show_neural_net():
    pass


def plot_all_scores():
    pass


def plot_high_scores():
    pass


tick_speed = 10000
while True:
    for snake in naturalSelector.current_population:  # TQDM loop
        print("generation: {} | snake: {}".format(current_gen, snake.ID))
        score = 0
        while snake.is_alive:

            tick_speed = get_game_inputs(tick_speed)

            if snake.move() == 1:
                score += 1
                print(score)

            window.fill(pygame.Color('white'))
            for pos in snake.get_body():
                pygame.draw.rect(window, pygame.Color(0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))
            pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(snake.foodLoc[0], snake.foodLoc[1], 10, 10))
            fps.tick(tick_speed)
            pygame.display.set_caption('neural snakes | generation {}'.format(current_gen))
            pygame.display.flip()

    generation_over(current_gen, naturalSelector.high_score)
    naturalSelector.create_new_population(3000, 100)
    current_gen += 1

    if current_gen >= number_of_generation:
        game_over()
