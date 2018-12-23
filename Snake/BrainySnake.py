import random
from NeuralNet.NeuralNet import *


class BrainSnake:
    def __init__(self, _id, gen=-1, width=500, height=500, pvp=False):
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

        self.foodLoc = [-1, -1]
        self.food_on_screen = False

        self.ID = _id
        self.gen = gen
        self.pvp = pvp

        self.brain_input = []
        self.distance_to_food = 0
        self.food_quadrant = [-1, -1]
        self.obstacles = [0] * 8

        self.local_fitness = 0
        self.global_fitness = 0

        self.sqrt2 = np.sqrt(2)
        self.wall_array = []

        self.update_wall_array()
        self.spawn_food()

        self.brain = Net()
        self.brain.save_model(gen, _id)

    def get_head_pos(self):
        return self.head

    def get_body(self):
        return self.body

    def get_food_pos(self):
        return self.foodLoc

    def change_dir_to(self, new_direction):
        if new_direction == 'RIGHT' and not self.direction == 'LEFT':
            self.direction = new_direction
        if new_direction == 'LEFT' and not self.direction == 'RIGHT':
            self.direction = new_direction
        if new_direction == 'UP' and not self.direction == 'DOWN':
            self.direction = new_direction
        if new_direction == 'DOWN' and not self.direction == 'UP':
            self.direction = new_direction

    def change_dir_neural(self):
        x = self.brain(torch.Tensor(self.brain_input))
        if x[0] > 0.5 < x[1]:
            self.dirNeural -= 1
        elif x[0] < 0.5 > x[1]:
            self.dirNeural += 1

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

    def move(self):
        if self.direction == "RIGHT":
            self.head[0] += 10
        if self.direction == "LEFT":
            self.head[0] -= 10
        if self.direction == "DOWN":
            self.head[1] += 10
        if self.direction == "UP":
            self.head[1] -= 10
        self.steps += 1
        self.steps_to_food += 1
        self.body.insert(0, list(self.head))
        if self.head == self.foodLoc:
            self.score += 1
            self.steps_to_food = 0
            self.food_on_screen = False
            if not self.pvp:
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

    def update_wall_array(self):
        self.wall_array = []
        for i in range(0, self.MaxHeight, 10):
            self.wall_array.append([-10, i])
            self.wall_array.append([self.MaxWidth, i])
        for i in range(0, self.MaxWidth, 10):
            self.wall_array.append([i, -10])
            self.wall_array.append([i, self.MaxHeight])

    def detect_obstacles(self):
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

        self.obstacles = [obstacle_north, obstacle_north_east, obstacle_east, obstacle_south_east, obstacle_south,
                          obstacle_south_west, obstacle_west, obstacle_north_west]

    def locate_food(self):

        if self.head[0] > self.foodLoc[0]:
            self.food_quadrant[0] = 1
        else:
            self.food_quadrant[0] = 0

        if self.head[1] > self.foodLoc[1]:
            self.food_quadrant[1] = 0
        else:
            self.food_quadrant[1] = 1

    def update_dist_to_food(self):
        a = self.head[0] - self.foodLoc[0]
        b = self.head[1] - self.foodLoc[1]
        self.distance_to_food = np.sqrt(a ** 2 + b ** 2)

    def update_brain_input(self):
        self.detect_obstacles()
        self.locate_food()
        self.update_dist_to_food()

        self.brain_input = self.obstacles + self.food_quadrant + [self.distance_to_food]

    def update_global_fitness(self):
        self.global_fitness = self.score * 1000 - (self.steps * 0.1) + ((1 / self.distance_to_food) * 1000)

    def update_local_fitness(self):
        self.local_fitness = (1 / self.distance_to_food) * 4000 - self.steps

    def update_fitness(self):
        self.update_local_fitness()
        self.update_global_fitness()
        # print(self.local_fitness, self.global_fitness)

    def terminate_function(self):
        if self.steps_to_food > 100:
            self.is_alive = False
            return 1
        else:
            return 0

    def spawn_food(self):
        if not self.food_on_screen:
            self.foodLoc = [random.randrange(0, self.MaxWidth / 10) * 10, random.randrange(0, self.MaxHeight / 10) * 10]
            self.food_on_screen = True