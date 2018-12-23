from Snake.Snake import *
from NeuralNet.NaturalSelection import *
from Snake.BrainySnake import *

network_dict = {0: {'mode': "Linear", "input": 11, "output": 12, "bias": True, "activation": "ReLU"},
                1: {'mode': "Linear", "input": -1, "output": 6, "bias": True, "activation": "Sigmoid"},
                2: {'mode': "Linear", "input": -1, "output": 4, "bias": True, "activation": "Sigmoid"},
                3: {'mode': "Linear", "input": -1, "output": 2, "bias": True, "activation": "ReLU6"}}

window = pygame.display.set_mode((300, 200))
pygame.display.set_caption("wow_snake")
fps = pygame.time.Clock()
score = 0
current_gen = 0
number_of_generation = 30

w, h = pygame.display.get_surface().get_size()
snake = Snake(0, -1, w, h)
foodSp = FoodSpawner(w, h)
naturalSelector = NaturalSelection(BrainSnake, w, h)
naturalSelector.generate_first_population(500)


def generation_over(gen, highscore):
    print('All snakes of generation {} are dead.'.format(gen))
    print("Best fitness score of generation {}: {}".format(gen, highscore))
    print('Making new snakes')


def gameOver():
    print('game over')
    pygame.quit()
    sys.exit()


# while True:
#     foodPos = foodSp.spawn_food()
#     snake.change_dir_neural()
#     if snake.move(foodPos) == 1:
#         score += 1
#         print('score:  ', score)
#         foodSp.set_food_on_screen(False)
#     window.fill(pygame.Color('white'))
#     for pos in snake.get_body():
#         pygame.draw.rect(window, pygame.Color(0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))
#     pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(foodPos[0], foodPos[1], 10, 10))
#     if snake.check_collision() == 1:
#         gameOver()
#     if snake.terminate_function():
#         gameOver()
#     pygame.display.set_caption('wow snake | score: ' + str(score))
#     pygame.display.flip()
#     fps.tick(2000)


dead = 0
while True:
    foodPos = foodSp.spawn_food()
    window.fill(pygame.Color('white'))
    for snake in naturalSelector.current_population:
        if snake.is_alive:
            snake.update_brain_input()
            snake.change_dir_neural()
            if snake.move() == 1:
                snake.update_fitness()
                snake.update_brain_input()
                foodSp.set_food_on_screen(False)
            for pos in snake.get_body():
                pygame.draw.rect(window, pygame.Color(0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))
            pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(snake.foodLoc[0], snake.foodLoc[1], 10, 10))
            snake.check_collision()
            snake.terminate_function()
            if not snake.is_alive:
                dead += 1
                # print('deadsnakes {}/{}'.format(dead,len(naturalSelector.current_population)))
        if dead == len(naturalSelector.current_population):
            generation_over(current_gen, naturalSelector.high_score)
            current_gen += 1
            naturalSelector.create_new_population(30, 10)
            dead = 0
    pygame.display.set_caption('neural snakes| generation {}'.format(current_gen))
    pygame.display.flip()
    fps.tick(10000)
    if current_gen >= number_of_generation:
        gameOver()
