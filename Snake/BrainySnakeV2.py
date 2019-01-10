import random
from NeuralNet.SimpleNN import *
import torch


class BrainSnake:
    def __init__(self, _id, gen=-1, width=500, height=500):
        self.MaxWidth = width
        self.MaxHeight = height
        self.ID = _id
        self.gen = gen

        self.static_food_loc = [[60, 60], [50, 20], [70, 40], [50, 70], [30, 60], [60, 80], [90, 90], [70, 50], [30, 10], [30, 30], [50, 70]]

        self.head = [50, 50]
        self.body = [[50, 50], [40, 50], [30, 50]]
        self.direction = "RIGHT"
        self.direction_map = {1: "RIGHT", 2: "DOWN", 3: "LEFT", 4: "UP"}
        self.dirNeural = 0
        self.is_alive = True

        self.steps = 0
        self.score = 0
        self.time_to_live = 130

        self.threshold = 0.6
        self.vision_range = 20
        self.input_scale = 10

        self.foodLoc = [-1, -1]
        self.food_on_screen = False
        self.dst_to_food = 0

        self.brain_input = [0.5] * 11
        self.food_quadrant = [-1, -1]
        self.obstacles = [0] * 8
        self.closest_obstacle = [0] * 8
        self.wall_array = []

        self.global_fitness = 0
        self.bonus = 0

        self.set_walls()
        self.spawn_food()

        self.brain = Policy()
        self.generate_brain_input()
        # self.optimizer = optim.Adam(self.brain.parameters(), lr=0.01)
        # self.eps = np.finfo(np.float32).eps.item()

    def reset(self):
        self.head = [50, 50]
        self.body = [[50, 50], [40, 50], [30, 50]]
        self.direction = "RIGHT"
        self.is_alive = True
        self.score = 0
        self.global_fitness = 0
        self.foodLoc = [-1, -1]
        self.food_on_screen = False
        self.spawn_food()

    def get_head_pos(self):
        return self.head

    def get_body(self):
        return self.body

    def get_food_pos(self):
        return self.foodLoc

    def set_walls(self):
        self.wall_array = []
        for i in range(0, self.MaxHeight, 10):
            self.wall_array.append([-10, i])
            self.wall_array.append([self.MaxWidth, i])
        for i in range(0, self.MaxWidth, 10):
            self.wall_array.append([i, -10])
            self.wall_array.append([i, self.MaxHeight])

    def select_action(self):
        probs = self.brain(torch.Tensor(self.brain_input))
        if probs[0] > probs[1] and probs[0] > 0.6:
            action = [1, 0]
        elif probs[1] > probs[0] and probs[1] > 0.6:
            action = [0, 1]
        else:
            action = [0, 0]
        return action

    def set_direction(self):
        action = self.select_action()
        cur_dir = None
        if action[0] == 1 and action[1] == 0:
            next_dir = "LEFT"
        elif action[0] == 0 and action[1] == 1:
            next_dir = "RIGHT"
        else:
            next_dir = None
        for i in self.direction_map:
            if self.direction_map[i] == self.direction:
                cur_dir = i
                break
        if next_dir == "LEFT":
            cur_dir -= 1
        elif next_dir == "RIGHT":
            cur_dir += 1
        else:
            cur_dir = cur_dir

        if cur_dir < 1:
            cur_dir = 4
        elif cur_dir > 4:
            cur_dir = 1

        self.direction = self.direction_map[cur_dir]

    def move(self):
        self.generate_brain_input()
        self.set_direction()
        if self.direction == "RIGHT":
            self.head[0] += 10
        if self.direction == "LEFT":
            self.head[0] -= 10
        if self.direction == "DOWN":
            self.head[1] += 10
        if self.direction == "UP":
            self.head[1] -= 10
        self.steps += 1
        self.time_to_live -= 1
        self.body.insert(0, list(self.head))
        dead = self.check_collision()
        if self.time_to_live < 0:
            self.terminate()
        if self.head == self.foodLoc:
            self.score += 1
            self.time_to_live = 10 * len(self.body) + 100
            self.food_on_screen = False
            self.spawn_food()
            self.update_fitness()
            return 1
        else:
            self.body.pop()
            self.update_fitness()
            return 0

    def check_collision(self):
        obst = self.wall_array + self.body[1:]
        if self.head in obst:
            self.terminate()
            return True
        return False

    def terminate(self):
        self.is_alive = False

    def spawn_food(self):
        if not self.food_on_screen:
            if self.score < 10:
                self.foodLoc = self.static_food_loc[self.score]
            else:
                while not self.food_on_screen:
                    self.foodLoc = [random.randrange(0, self.MaxWidth / 10) * 10, random.randrange(0, self.MaxHeight / 10) * 10]
                    if self.foodLoc not in self.body:
                        self.food_on_screen = True
            # self.food_on_screen = True

    def locate_food(self):
        if self.head[0] > self.foodLoc[0]:
            self.food_quadrant[0] = 1
        else:
            self.food_quadrant[0] = 0

        if self.head[1] > self.foodLoc[1]:
            self.food_quadrant[1] = 0
        else:
            self.food_quadrant[1] = 1

        a = self.head[0] - self.foodLoc[0]
        b = self.head[1] - self.foodLoc[1]
        self.dst_to_food = self.input_scale/(np.sqrt(a ** 2 + b ** 2))

    def detect_obstacles(self):
        obstacle_array = self.body[1:] + self.wall_array

        north = []
        east = []
        south = []
        west = []

        for item in obstacle_array:
            if self.head[0] == item[0] and self.vision_range >= self.head[1] - item[1] > 0:
                north.append(self.head[1] - item[1])
            elif self.head[0] == item[0] and self.vision_range >= item[1] - self.head[1] > 0:
                south.append(item[1] - self.head[1])
            elif self.head[1] == item[1] and self.vision_range >= item[0] - self.head[0] > 0:
                east.append(item[0] - self.head[0])
            elif self.head[1] == item[1] and self.vision_range >= self.head[0] - item[0] > 0:
                west.append(self.head[0] - item[0])

        obstacle_north = self.input_scale / min(north) if len(north) is not 0 else 0
        obstacle_east = self.input_scale / min(east) if len(east) is not 0 else 0
        obstacle_south = self.input_scale / min(south) if len(south) is not 0 else 0
        obstacle_west = self.input_scale / min(west) if len(west) is not 0 else 0

        self.closest_obstacle = [obstacle_north, obstacle_east, obstacle_south, obstacle_west]

    def generate_brain_input(self):
        self.locate_food()
        self.detect_obstacles()
        self.brain_input = self.closest_obstacle + self.food_quadrant + [self.dst_to_food]

    def update_global_fitness(self):
        self.bonus = self.bonus + 1
        self.global_fitness = (self.score * 1000) + self.bonus

    def update_fitness(self):
        self.update_global_fitness()
