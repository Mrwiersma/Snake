import random
import torch
from NeuralNet.NeuralNet import *


class BrainSnake:
    def __init__(self, _id, gen=-1, width=500, height=500, pvp=False, network_layout=None):
        self.MaxWidth = width
        self.MaxHeight = height

        self.head = [50, 50]
        self.body = [[50, 50], [40, 50], [30, 50]]
        self.direction = "RIGHT"
        self.dirNeural = 0
        self.is_alive = True
        self.score = 0
        self.steps = 0
        self.steps_to_food = 0
        self.threshold = 0.6

        self.foodLoc = [-1, -1]
        self.food_on_screen = False

        self.ID = _id
        self.gen = gen
        self.pvp = pvp

        self.brain_input = []
        self.distance_to_food = 0
        self.prev_dist_to_food = 0
        self.mean_dist = [0] * 10
        self.food_quadrant = [-1, -1]
        self.obstacles = [0] * 8

        self.local_fitness = 0
        self.global_fitness = 0

        self.sqrt2 = np.sqrt(2)
        self.wall_array = []

        self.update_wall_array()
        self.spawn_food()

        if network_layout is not None:
            self.brain = Net(network_layout)
        else:
            self.brain = Net()

        if torch.cuda.is_available():
            #cuda0 = torch.device("cuda:0")
            self.brain.cuda()
        # self.brain.save_model(gen, _id)

    def get_head_pos(self):
        return self.head

    def get_body(self):
        return self.body

    def get_food_pos(self):
        return self.foodLoc

    def change_dir_to(self, new_direction):  # zet uiteindelijke richting rekening houdend met bestaande richting
        if new_direction == 'RIGHT' and not self.direction == 'LEFT':
            self.direction = new_direction
        if new_direction == 'LEFT' and not self.direction == 'RIGHT':
            self.direction = new_direction
        if new_direction == 'UP' and not self.direction == 'DOWN':
            self.direction = new_direction
        if new_direction == 'DOWN' and not self.direction == 'UP':
            self.direction = new_direction

    @staticmethod
    def calc_chance(x):
        y = np.random.uniform(0, 1)
        if x > 0.5 and x > y:
            return 1
        else:
            return 0

    def change_dir_neural(self):  # vertaalt NN output tot richting
        x = self.brain(torch.Tensor(self.brain_input))

        do_we_move_left = self.calc_chance(x[0])
        do_we_move_right = self.calc_chance(x[1])

        if do_we_move_left == 1 and do_we_move_right == 0:
            self.dirNeural -= 1
        elif do_we_move_right == 1 and do_we_move_left == 0:
            self.dirNeural += 1
        # # x = x.detach().numpy()
        # if x[0] > x[1] and x[0] > self.threshold:
        #     self.dirNeural -= 1
        #
        # elif x[1] > x[0] and x[1] > self.threshold:
        #     self.dirNeural += 1

        if self.dirNeural < 0:
            self.dirNeural = 3
        elif self.dirNeural > 3:
            self.dirNeural = 0

        if self.dirNeural == 0:
            self.direction = "RIGHT"
        elif self.dirNeural == 1:
            self.direction = "DOWN"
        elif self.dirNeural == 2:
            self.direction = "LEFT"
        elif self.dirNeural == 3:
            self.direction = "UP"

    def move(self):  # snake doet een stap  en kijkt of hij eten heeft gevonden
        if self.direction == "RIGHT":
            self.head[0] += 10
        if self.direction == "LEFT":
            self.head[0] -= 10
        if self.direction == "DOWN":
            self.head[1] += 10
        if self.direction == "UP":
            self.head[1] -= 10
        self.steps += 1  # totaal aantal stappen
        self.steps_to_food += 1  # stappen sinds vorige eten
        self.body.insert(0, list(self.head))
        if self.head == self.foodLoc:
            self.score += 1
            self.steps_to_food = 0
            self.food_on_screen = False
            self.spawn_food()
            return 1
        else:
            self.body.pop()
            return 0

    def check_collision(self):
        if self.head[0] >= self.MaxWidth or self.head[0] < 0:
            self.is_alive = False
            return 1
        elif self.head[1] >= self.MaxHeight or self.head[1] < 0:
            self.is_alive = False
            return 1
        for bodypart in self.body[1:]:
            if self.head == bodypart:
                self.is_alive = False
                return 1
        return 0

    def update_wall_array(self):  # is nodig voor obstakel detectie, maakt een lijst met alle muren
        self.wall_array = []
        for i in range(0, self.MaxHeight, 10):
            self.wall_array.append([-10, i])
            self.wall_array.append([self.MaxWidth, i])
        for i in range(0, self.MaxWidth, 10):
            self.wall_array.append([i, -10])
            self.wall_array.append([i, self.MaxHeight])

    def detect_obstacles(self):  # geeft per richting de dichtbijzijnste obstakel
        obstacle_array = self.body[1:] + self.wall_array

        north = []
        northeast = []
        east = []
        southeast = []
        south = []
        southwest = []
        west = []
        northwest = []

        for item in obstacle_array:
            if self.head[0] == item[0] and self.head[1] - item[1] > 0:
                north.append(self.head[1] - item[1])
            elif self.head[0] == item[0] and item[1] - self.head[1] > 0:
                south.append(item[1] - self.head[1])
            elif self.head[1] == item[1] and item[0] - self.head[0] > 0:
                east.append(item[0] - self.head[0])
            elif self.head[1] == item[1] and self.head[0] - item[0] > 0:
                west.append(self.head[0] - item[0])

            elif self.head[1] - item[1] == self.head[0] - item[0] and (self.head[1] - item[1]) * self.sqrt2 > 0:
                northwest.append((self.head[1] - item[1]) * self.sqrt2)
            elif item[1] - self.head[1] == self.head[0] - item[0] and (item[1] - self.head[1]) * self.sqrt2 > 0:
                southwest.append((item[1] - self.head[1]) * self.sqrt2)
            elif item[1] - self.head[1] == item[0] - self.head[0] and (item[1] - self.head[1]) * self.sqrt2 > 0:
                southeast.append((item[1] - self.head[1]) * self.sqrt2)
            elif self.head[1] - item[1] == item[0] - self.head[0] and (self.head[1] - item[1]) * self.sqrt2 > 0:
                northeast.append((self.head[1] - item[1]) * self.sqrt2)

        obstacle_north = min(north) if len(north) is not 0 else -1
        obstacle_north_east = min(northeast) if len(northeast) is not 0 else -1
        obstacle_east = min(east) if len(east) is not 0 else -1
        obstacle_south_east = min(southeast) if len(southeast) is not 0 else -1
        obstacle_south = min(south) if len(south) is not 0 else -1
        obstacle_west = min(west) if len(west) is not 0 else -1
        obstacle_south_west = min(southwest) if len(southwest) is not 0 else -1
        obstacle_north_west = min(northwest) if len(northwest) is not 0 else -1

        self.obstacles = [10 / obstacle_north, 10 / obstacle_north_east, 10 / obstacle_east, 10 / obstacle_south_east,
                          10 / obstacle_south,
                          10 / obstacle_south_west, 10 / obstacle_west, 10 / obstacle_north_west]

    def locate_food(self):  # geeft aan of het eten boven/onder link/rechts van de snake ligt

        if self.head[0] > self.foodLoc[0]:
            self.food_quadrant[0] = 1
        else:
            self.food_quadrant[0] = 0

        if self.head[1] > self.foodLoc[1]:
            self.food_quadrant[1] = 0
        else:
            self.food_quadrant[1] = 1

    def update_dist_to_food(self):  # berekend afstand tot eten
        a = self.head[0] - self.foodLoc[0]
        b = self.head[1] - self.foodLoc[1]
        self.distance_to_food = np.sqrt(a ** 2 + b ** 2)

    def update_brain_input(self):  # roept bovenstaande functies aan
        self.detect_obstacles()
        self.locate_food()
        self.update_dist_to_food()
        self.brain_input = self.obstacles + self.food_quadrant + [(10 / self.distance_to_food)]  # uiteindelijke input van het NN

    def update_global_fitness(self):  # fitness functies die nog nerggens op slaan

        self.mean_dist.insert(0, self.prev_dist_to_food - self.distance_to_food)
        self.mean_dist.pop()

        if self.steps > len(self.mean_dist):
            self.global_fitness += np.mean(self.mean_dist) * 2

        if self.score > 0:
            self.global_fitness += 500 * self.score
            self.score = 0
        self.global_fitness += self.steps ** (1 / 10)  # lifetime bonus
        self.prev_dist_to_food = self.distance_to_food

    def update_local_fitness(self):  # slaat ook nog nergens op
        self.local_fitness = (1 / 1 + self.distance_to_food) * 4000 - self.steps

    def update_fitness(self):  # update beide fitnesses tegelijk
        self.update_local_fitness()
        self.update_global_fitness()
        # print(self.rewards, self.global_fitness)

    def terminate_function(self):  # kijkt of snake niet te lang niks gegeten heeft
        if self.steps_to_food > 100 + len(self.body) * 50:
            self.is_alive = False
            return 1
        else:
            return 0

    def spawn_food(self):  # maakt het eten voor de slang
        if not self.food_on_screen:
            self.foodLoc = [random.randrange(0, self.MaxWidth / 10) * 10, random.randrange(0, self.MaxHeight / 10) * 10]
            self.food_on_screen = True
