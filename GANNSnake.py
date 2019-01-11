import pygame
import sys
from NeuralNet.NaturalSelectionV2 import *
from Snake.BrainySnakeV2 import *
from Snake_visualizer import *

network_dict = {0: {'mode': "Linear", "input": 11, "output": 16, "bias": True, "activation": "Sigmoid", "activation_params": []},
                1: {'mode': "Linear", "input": -1, "output": 2, "bias": True, "activation": "Sigmoid",
                    "activation_params": [0, 1, False]}}

window = pygame.display.set_mode((1000, 800))

pygame.display.set_caption("wow_snake")
fps = pygame.time.Clock()

current_gen = 0
number_of_generation = 80

# w, h = pygame.display.get_surface().get_size()
naturalSelector = NaturalSelection(BrainSnake, 100, 100)
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


def set_game_tick(step, cur_tick):
    tick = cur_tick
    tick += step
    if tick <= 0:
        tick = 10
    print(tick)
    return tick


def plot_all_scores(ranked=True):
    pass


def plot_high_scores(gen):
    pass


tick_speed = 10000
show_info = True
show_vision = False
general_info = GeneralVisualiser(window, origin=(0, 0))
while True:

    window.fill(pygame.Color("white"))
    general_info.show_general_info(current_gen)
    pygame.display.set_caption('neural snakes | generation {}'.format(current_gen))

    for snake in naturalSelector.current_population:  # TQDM loop
        print("generation: {} | snake: {}".format(current_gen, snake.ID))
        score = 0
        visualizer = SnakeVisualizer(snake, window, origin=(10, 25))
        while snake.is_alive:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_PAGEDOWN:
                        tick_speed = set_game_tick(-1000, tick_speed)
                    if event.key == pygame.K_PAGEUP:
                        tick_speed = set_game_tick(1000, tick_speed)
                    if event.key == pygame.K_UP:
                        tick_speed = set_game_tick(10, tick_speed)
                    if event.key == pygame.K_DOWN:
                        tick_speed = set_game_tick(-10, tick_speed)
                    if event.key == pygame.K_LEFT:
                        tick_speed = set_game_tick(1, tick_speed)
                    if event.key == pygame.K_RIGHT:
                        tick_speed = set_game_tick(-1, tick_speed)
                    if event.key == pygame.K_v:
                        show_vision = not show_vision
                    if event.key == pygame.K_i:
                        show_info = not show_info

            if snake.move() == 1:
                score += 1
                print(score)

            visualizer.show_snake()
            if show_vision:
                visualizer.show_snake_vision()
            if show_info:
                visualizer.show_info()

            fps.tick(tick_speed)
            pygame.display.flip()

    generation_over(current_gen, naturalSelector.high_score)
    naturalSelector.create_new_population(3000, 100)
    current_gen += 1

    if current_gen >= number_of_generation:
        game_over()
