import random
from Old.NeuralNet import *


class Snake:
    def __init__(self, _id, gen=-1, width=500, height=500):
        self.head = [50, 50]
        self.body = [[50, 50], [40, 50], [30, 50]]
        self.direction = "RIGHT"
        self.dirNeural = 0
        self.changeDirTo = self.direction
        self.MaxWidth = width
        self.MaxHeight = height
        self.ID = _id
        self.is_alive = True

        self.score = 0
        self.step_bonus = 0
        self.proxy_bonus = 0
        self.steps = 0
        self.fitness = 0
        self.terminate = 100
        self.dist_to_food = 0
        self.awareness_array = [0] * 8 * 3
        self.food = [-1, -1]
        self.food_on_screen = False

        self.sqrt2 = np.sqrt(2)

        self.update_awareness()
        self.update_fitness()

        self.brain = Net()

    def set_max_height(self, x):
        self.MaxHeight = x

    def set_max_width(self, x):
        self.MaxWidth = x

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
        x = self.brain(torch.Tensor(self.awareness_array))
        # print("output: ", x)
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

    def move(self, foodPos):
        self.food = foodPos
        # print(self.awareness(foodPos)[-8:])
        if self.direction == "RIGHT":
            self.head[0] += 10
        if self.direction == "LEFT":
            self.head[0] -= 10
        if self.direction == "DOWN":
            self.head[1] += 10
        if self.direction == "UP":
            self.head[1] -= 10
        self.body.insert(0, list(self.head))
        self.steps += 1
        self.update_awareness()
        self.update_proxy_bonus()
        self.update_fitness()
        if self.head == self.food:
            self.score += 1
            self.step_bonus = self.step_bonus + (100 - self.steps)
            self.update_terminate()
            self.food_on_screen = False
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

    def distance_to_food(self):
        a = self.head[0] - self.food[0]
        b = self.head[1] - self.food[1]
        self.dist_to_food = np.sqrt(a ** 2 + b ** 2)

    def update_proxy_bonus(self):
        self.distance_to_food()
        self.proxy_bonus = (1 / (1 + self.dist_to_food))  *1000

    def get_head_pos(self):
        return self.head

    def get_body(self):
        return self.body

    def update_foosPos(self, foodpos):
        self.food = foodpos
        self.food_on_screen = True

    def update_awareness(self):
        wall_north = self.head[1]
        wall_east = self.MaxWidth - self.head[0]
        wall_south = self.MaxWidth - self.head[1]
        wall_west = self.head[0]
        wall_north_east = wall_north * self.sqrt2 if wall_north <= wall_east else wall_east * self.sqrt2
        wall_south_east = wall_south * self.sqrt2 if wall_south <= wall_east else wall_east * self.sqrt2
        wall_south_west = wall_south * self.sqrt2 if wall_south <= wall_west else wall_west * self.sqrt2
        wall_north_west = wall_north * self.sqrt2 if wall_north <= wall_west else wall_west * self.sqrt2

        food_north = self.head[1] - self.food[1] if self.head[0] == self.food[0] and self.head[1] - self.food[1] >= 0 else -1
        food_east = self.head[0] - self.food[0] if self.head[1] == self.food[1] and self.head[0] - self.food[0] >= 0 else -1
        food_south = self.food[1] - self.head[1] if self.head[0] == self.food[0] and self.food[1] - self.head[1] >= 0 else -1
        food_west = self.food[0] - self.head[0] if self.head[1] == self.food[1] and self.food[0] - self.head[0] >= 0 else -1
        food_north_east = (self.head[1] - self.food[1]) * self.sqrt2 if self.head[1] - self.food[1] == self.head[0] - self.food[0] \
                                                                        and (self.head[1] - self.food[
            1]) * self.sqrt2 >= 0 else -1
        food_south_east = (self.food[1] - self.head[1]) * self.sqrt2 if self.food[1] - self.head[1] == self.head[0] - self.food[0] \
                                                                        and (self.food[1] - self.head[
            1]) * self.sqrt2 >= 0 else -1
        food_south_west = (self.food[1] - self.head[1]) * self.sqrt2 if self.food[1] - self.head[1] == self.food[0] - self.head[0] \
                                                                        and (self.food[1] - self.head[
            1]) * self.sqrt2 >= 0 else -1
        food_north_west = (self.head[1] - self.food[1]) * self.sqrt2 if self.head[1] - self.food[1] == self.food[0] - self.head[0] \
                                                                        and (self.head[1] - self.food[
            1]) * self.sqrt2 >= 0 else -1

        north = []
        northeast = []
        east = []
        southeast = []
        south = []
        southwest = []
        west = []
        northwest = []

        for item in self.body[1:]:
            if self.head[0] == item[0] and self.head[1] - item[1] >= 0:
                north.append(self.head[1] - item[1])
            elif self.head[1] == item[1] and self.head[0] - item[0] >= 0:
                east.append(self.head[0] - item[0])
            elif self.head[0] == item[0] and item[1] - self.head[1] >= 0:
                south.append(item[1] - self.head[1])
            elif self.head[1] == item[1] and item[0] - self.head[0] >= 0:
                west.append(item[0] - self.head[0])
            elif self.head[1] - item[1] == self.head[0] - item[0] and (self.head[1] - item[1]) * self.sqrt2:
                northeast.append((self.head[1] - item[1]) * self.sqrt2)
            elif item[1] - self.head[1] == self.head[0] - item[0] and (item[1] - self.head[1]) * self.sqrt2:
                southeast.append((item[1] - self.head[1]) * self.sqrt2)
            elif item[1] - self.head[1] == item[0] - self.head[0] and (item[1] - self.head[1]) * self.sqrt2:
                southwest.append((item[1] - self.head[1]) * self.sqrt2)
            elif self.head[1] - item[1] == item[0] - self.head[0] and (self.head[1] - item[1]) * self.sqrt2:
                northwest.append((self.head[1] - item[1]) * self.sqrt2)

        self_north = min(north) if len(north) is not 0 else -1
        self_north_east = min(northeast) if len(northeast) is not 0 else -1
        self_east = min(east) if len(east) is not 0 else -1
        self_south_east = min(southeast) if len(southeast) is not 0 else -1
        self_south = min(south) if len(south) is not 0 else -1
        self_west = min(west) if len(west) is not 0 else -1
        self_south_west = min(southwest) if len(southwest) is not 0 else -1
        self_north_west = min(northwest) if len(northwest) is not 0 else -1

        self.awareness_array = [wall_north, wall_north_east, wall_east, wall_south_east, wall_south, wall_south_west, wall_west,
                                wall_north_west,
                                food_north, food_north_east, food_east, food_south_east, food_south, food_south_west, food_west,
                                food_north_west,
                                self_north, self_north_east, self_east, self_south_east, self_south, self_south_west, self_west,
                                self_north_west]

    def update_fitness(self):
        self.fitness = 100 + (self.score * 100) + self.step_bonus + self.proxy_bonus
        # print(self.proxy_bonus)
        #print(self.fitness)

    def update_terminate(self):
        self.terminate = len(self.body) + 100
        self.steps = 0

    def terminate_function(self):
        if self.terminate - self.steps < 0:
            self.is_alive = False
            return 1
        else:
            return 0


class FoodSpawner:
    def __init__(self, width=500, height=500):
        self.position = [random.randrange(1, (width / 10)) * 10, random.randrange(1, (height / 10)) * 10]
        self.FoodIsOnScreen = True
        self.width = width / 10
        self.height = height / 10

    def spawn_food(self):
        if not self.FoodIsOnScreen:
            self.position = [random.randrange(1, self.width) * 10, random.randrange(1, self.height) * 10]
            self.FoodIsOnScreen = True
        return self.position

    def set_food_on_screen(self, b):
        self.FoodIsOnScreen = b
