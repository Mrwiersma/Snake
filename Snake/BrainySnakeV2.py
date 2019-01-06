import random
from NeuralNet.SimpleNN import *
from torch.distributions import Categorical
import torch


class BrainSnake:
    def __init__(self, _id, gen=-1, width=500, height=500, network_layout=None):
        self.MaxWidth = width
        self.MaxHeight = height

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
        self.scale = 1

        self.foodLoc = [-1, -1]
        self.food_on_screen = False
        self.dst_to_food = 0

        self.ID = _id
        self.gen = gen

        self.brain_input = [0.5] * 11
        self.food_quadrant = [-1, -1]
        self.obstacles = [0] * 8
        self.closest_obstacle = [0] * 8
        self.wall_array = []

        self.rewards = []
        self.global_fitness = 0

        self.sqrt2 = np.sqrt(2)

        self.set_walls()
        self.spawn_food()

        self.brain = Policy()
        self.generate_brain_input()
        self.optimizer = optim.Adam(self.brain.parameters(), lr=0.01)
        self.eps = np.finfo(np.float32).eps.item()
        self.bonus = 0

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
        # if (probs[0] > 0 and probs[1] > 0) or (probs[0] <0 and probs[1] < 0):
        m = Categorical(probs)
        action = m.sample([2])
        self.brain.saved_log_probs.append(m.log_prob(action))
        return action

    # def finish_episode(self):
    #     R = 0
    #     policy_loss = []
    #     rewards = []
    #     for r in self.brain.rewards[::-1]:
    #         R = r + 0.8 * R
    #         rewards.insert(0, R)
    #     rewards = torch.tensor(rewards)
    #     rewards = (rewards) / (rewards.std() + self.eps)
    #     for log_prob, reward in zip(self.brain.saved_log_probs, rewards):
    #         policy_loss.append(-log_prob * reward)
    #     self.optimizer.zero_grad()
    #     policy_loss = torch.cat(policy_loss).sum()
    #     print(" pol: {} \n".format(policy_loss))
    #     policy_loss.backward()
    #     self.optimizer.step()
    #     del self.brain.rewards[:]
    #     del self.brain.saved_log_probs[:]

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
        # if new_direction == 'RIGHT' and not self.direction == 'LEFT':
        #     self.direction = new_direction
        # if new_direction == 'LEFT' and not self.direction == 'RIGHT':
        #     self.direction = new_direction
        # if new_direction == 'UP' and not self.direction == 'DOWN':
        #     self.direction = new_direction
        # if new_direction == 'DOWN' and not self.direction == 'UP':
        #     self.direction = new_direction

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
        # if self.steps % 20 == 0:
        #     self.finish_episode()
        if self.head == self.foodLoc:
            self.score += 1
            self.time_to_live = 10 * len(self.body) + 100
            self.food_on_screen = False
            self.spawn_food()
            # self.give_reward(True, dead)
            self.update_fitness()
            return 1
        else:
            self.body.pop()
            # self.give_reward(False, dead)
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
        # self.finish_episode()

    def spawn_food(self):
        if not self.food_on_screen:
            self.foodLoc = [random.randrange(0, self.MaxWidth / 10) * 10, random.randrange(0, self.MaxHeight / 10) * 10]
            self.food_on_screen = True

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
        self.dst_to_food = np.sqrt(a ** 2 + b ** 2)

    def detect_obstacles(self):
        obstacle_array = self.body[1:] + self.wall_array

        north = []
        east = []
        south = []
        west = []

        for item in obstacle_array:
            if self.head[0] == item[0] and self.head[1] - item[1] > 0:
                north.append(self.head[1] - item[1])
            elif self.head[0] == item[0] and item[1] - self.head[1] > 0:
                south.append(item[1] - self.head[1])
            elif self.head[1] == item[1] and item[0] - self.head[0] > 0:
                east.append(item[0] - self.head[0])
            elif self.head[1] == item[1] and self.head[0] - item[0] > 0:
                west.append(self.head[0] - item[0])

        obstacle_north = min(north) if len(north) is not 0 else -1
        obstacle_east = min(east) if len(east) is not 0 else -1
        obstacle_south = min(south) if len(south) is not 0 else -1
        obstacle_west = min(west) if len(west) is not 0 else -1

        self.closest_obstacle = [self.scale / obstacle_north, self.scale / obstacle_east, self.scale / obstacle_south, self.scale / obstacle_west]

    def generate_brain_input(self):
        self.locate_food()
        self.detect_obstacles()
        self.brain_input = self.closest_obstacle + self.food_quadrant + [(self.scale / self.dst_to_food)]

    def update_global_fitness(self):
        self.bonus = self.bonus + 1
        self.global_fitness = (len(self.body) * 1000) - 3000 + self.bonus
        # print(self.global_fitness)
        # print(self.brain.rewards)

        # def give_reward(self, food, dead):
        #     food_bonus = 0
        #     dead_penalty = 0
        # prev_dst = self.dst_to_food
        # self.locate_food()
        # progress = prev_dst - self.dst_to_food

    #     if progress < 0:
    #         progress = progress * 2
    #     if food:
    #         food_bonus = 1000
    #     if dead:
    #         dead_penalty = 10000
    #     reward = progress + food_bonus - dead_penalty
    #     self.brain.rewards.append(reward)

    def update_fitness(self):
        self.update_global_fitness()
