from Old.Snake import *
from NeuralNet.NaturalSelection import *
from Snake.BrainySnake import *

# input van het netwerk moet 11 blijven in de eerste laag (gelijk aan de lengte van de Brain_input array in een snake)
# output van het netwerk moet 2 blijven in de laatste laag (zie uitwerking in brainysnake.change_dir_neural)
# -1 betekend dat het de inputs geleik zet aan de outputs van de vorige laag
network_dict = {0: {'mode': "Linear", "input": 11, "output": 12, "bias": True, "activation": "ReLU"},
                1: {'mode': "Linear", "input": -1, "output": 6, "bias": True, "activation": "Sigmoid"},
                2: {'mode': "Linear", "input": -1, "output": 4, "bias": True, "activation": "Sigmoid"},
                3: {'mode': "Linear", "input": -1, "output": 2, "bias": True, "activation": "ReLU6"}}

window = pygame.display.set_mode((300, 200))  # groote van t scherm
# (pas op als je dit te klein maakt dan spawned de snake buiten het veld is is die direct dood)

pygame.display.set_caption("wow_snake")
fps = pygame.time.Clock()

current_gen = 0  # start in gen 0
number_of_generation = 30

w, h = pygame.display.get_surface().get_size()
naturalSelector = NaturalSelection(BrainSnake, w, h)  # init van het Genetic alg, args ( object, breedte scherm, hoogte scherm)
naturalSelector.set_nn_layout(network_dict)  # zet de layout van het NeuralNetwerk wat de Snake gebruikt. (zie network_dict)
naturalSelector.generate_first_population(500)  # first pop


def generation_over(gen, highscore):
    print('All snakes of generation {} are dead.'.format(gen))
    print("Best fitness score of generation {}: {}".format(gen, highscore))
    print('Making new snakes')


def gameOver():
    print('game over')
    pygame.quit()
    sys.exit()


dead = 0  # set dead snakes to 0
while True:
    window.fill(pygame.Color('white'))
    for snake in naturalSelector.current_population:
        if snake.is_alive:
            snake.update_brain_input()
            snake.change_dir_neural()
            if snake.move() == 1:
                snake.update_fitness()
                snake.update_brain_input()
            for pos in snake.get_body():
                pygame.draw.rect(window, pygame.Color(0, 255, 0), pygame.Rect(pos[0], pos[1], 10, 10))
            pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(snake.foodLoc[0], snake.foodLoc[1], 10, 10))
            snake.check_collision()  # kijkt of de snake niet met zn kop tegen iets aan beukt
            snake.terminate_function()  # kijk of de snake niet doelloos rond draaid
            if not snake.is_alive:
                dead += 1  # counts ded sneks
                # print('deadsnakes {}/{}'.format(dead,len(naturalSelector.current_population)))
        if dead == len(naturalSelector.current_population):  # als iedereen dood is is generatie over
            generation_over(current_gen, naturalSelector.high_score)
            current_gen += 1
            naturalSelector.create_new_population(30, 10)  # maakt nieuwe pop args(children,elite)
            # LETOP uiteindelijke pop is 2x children + elite
            dead = 0
    pygame.display.set_caption('neural snakes| generation {}'.format(current_gen))
    pygame.display.flip()
    fps.tick(10000)  # max speed of a game
    if current_gen >= number_of_generation:
        gameOver()
