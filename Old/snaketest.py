import random
import pygame
import sys
import time
import numpy as np


class Snake:
    def __init__(self):
        self.head = [100, 50]
        self.body = [[100, 50], [90, 50], [80, 50]]
        self.direction = "RIGHT"
        self.changeDirTo = self.direction
        self.MaxWidth = 500
        self.MaxHeight = 500

        self.FoodNorth = 0
        self.FoodNorthEast = 0
        self.FoodEast = 0
        self.FoodSouthEast = 0
        self.FoodSouth = 0
        self.FoodWest = 0
        self.FoodSouthWest = 0
        self.FoodNorthWest = 0

        self.WallNorth = 0
        self.WallNorthEast = 0
        self.WallEast = 0
        self.WallSouthEast = 0
        self.WallSouth = 0
        self.WallWest = 0
        self.WallSouthWest = 0
        self.WallNorthWest = 0

        self.SelfNorth = -1
        self.SelfNorthEast = -1
        self.SelfEast = -1
        self.SelfSouthEast = -1
        self.SelfSouth = -1
        self.SelfWest = -1
        self.SelfSouthWest = -1
        self.SelfNorthWest = -1

        self.sqrt2 = np.sqrt(2)

    def set_max_height(self, x):
        self.MaxHeight = x

    def set_max_width(self, x):
        self.MaxWidth = x

    def change_dir_to(self, dir):
        if dir == 'RIGHT' and not self.direction == 'LEFT':
            self.direction = dir
        if dir == 'LEFT' and not self.direction == 'RIGHT':
            self.direction = dir
        if dir == 'UP' and not self.direction == 'DOWN':
            self.direction = dir
        if dir == 'DOWN' and not self.direction == 'UP':
            self.direction = dir

    def move(self, foodPos):
        self.distance_to_food(foodPos)
        if self.direction == "RIGHT":
            self.head[0] += 10
        if self.direction == "LEFT":
            self.head[0] -= 10
        if self.direction == "DOWN":
            self.head[1] += 10
        if self.direction == "UP":
            self.head[1] -= 10
        self.body.insert(0, list(self.head))
        if self.head == foodPos:
            return 1
        else:
            self.body.pop()
            return 0

    def distance_to_food(self,food):
        a = self.head[0] - food[0]
        b = self.head[1] - food[1]
        dist_to_food = np.sqrt(a ** 2 + b ** 2)
        print(dist_to_food)

    def check_collision(self):
        if self.head[0] >= self.MaxWidth or self.head[0] < 0:
            return 1
        elif self.head[1] >= self.MaxHeight or self.head[1] < 0:
            return 1
        for bodypart in self.body[1:]:
            if self.head == bodypart:
                return 1
        return 0

    def get_head_pos(self):
        return self.head

    def get_body(self):
        return self.body

    def sences(self, foodPos):
        self.WallNorth = self.head[1]
        self.WallEast = self.MaxWidth - self.head[0]
        self.WallSouth = self.MaxWidth - self.head[1]
        self.WallWest = self.head[0]
        self.WallNorthEast = self.WallNorth * self.sqrt2 if self.WallNorth <= self.WallEast else self.WallEast * self.sqrt2
        self.WallSouthEast = self.WallSouth * self.sqrt2 if self.WallSouth <= self.WallEast else self.WallEast * self.sqrt2
        self.WallSouthWest = self.WallSouth * self.sqrt2 if self.WallSouth <= self.WallWest else self.WallWest * self.sqrt2
        self.WallNorthWest = self.WallNorth * self.sqrt2 if self.WallNorth <= self.WallWest else self.WallWest * self.sqrt2

        self.FoodNorth = self.head[1] - foodPos[1] if self.head[0] == foodPos[0] and self.head[1] - foodPos[1] >= 0 else -1
        self.FoodEast = self.head[0] - foodPos[0] if self.head[1] == foodPos[1] and self.head[0] - foodPos[0] >= 0 else -1
        self.FoodSouth = foodPos[1] - self.head[1] if self.head[0] == foodPos[0] and foodPos[1] - self.head[1] >= 0 else -1
        self.FoodWest = foodPos[0] - self.head[0] if self.head[1] == foodPos[1] and foodPos[0] - self.head[0] >= 0 else -1
        self.FoodNorthEast = (self.head[1] - foodPos[1]) * self.sqrt2 if self.head[1] - foodPos[1] == self.head[0] - foodPos[0] \
                                                                         and (self.head[1] - foodPos[1]) * self.sqrt2 >= 0 else -1
        self.FoodSouthEast = (foodPos[1] - self.head[1]) * self.sqrt2 if foodPos[1] - self.head[1] == self.head[0] - foodPos[0] \
                                                                         and (foodPos[1] - self.head[1]) * self.sqrt2 >= 0 else -1
        self.FoodSouthWest = (foodPos[1] - self.head[1]) * self.sqrt2 if foodPos[1] - self.head[1] == foodPos[0] - self.head[0] \
                                                                         and (foodPos[1] - self.head[1]) * self.sqrt2 >= 0 else -1
        self.FoodNorthWest = (self.head[1] - foodPos[1]) * self.sqrt2 if self.head[1] - foodPos[1] == foodPos[0] - self.head[0] \
                                                                         and (self.head[1] - foodPos[1]) * self.sqrt2 >= 0 else -1

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

            self.SelfNorth = min(north) if len(north) is not 0 else -1
            self.SelfNorthEast = min(northeast) if len(northeast) is not 0 else -1
            self.SelfEast = min(east) if len(east) is not 0 else -1
            self.SelfSouthEast = min(southeast) if len(southeast) is not 0 else -1
            self.SelfSouth = min(south) if len(south) is not 0 else -1
            self.SelfWest = min(west) if len(west) is not 0 else -1
            self.SelfSouthWest = min(southwest) if len(southwest) is not 0 else -1
            self.SelfNorthWest = min(northwest) if len(northwest) is not 0 else -1



class FoodSpawner:
    def __init__(self):
        self.position = [random.randrange(1, 50) * 10, random.randrange(1, 50) * 10]
        self.FoodIsOnScreen = True

    def spawn_food(self):
        if not self.FoodIsOnScreen:
            self.position = [random.randrange(1, 50) * 10, random.randrange(1, 50) * 10]
            self.FoodIsOnScreen = True
        return self.position

    def set_food_on_screen(self, b):
        self.FoodIsOnScreen = b


window = pygame.display.set_mode((500, 500))
pygame.display.set_caption("wow_snake")
fps = pygame.time.Clock()
score = 0

snake = Snake()
foodSp = FoodSpawner()
w, h = pygame.display.get_surface().get_size()
snake.set_max_height(h)
snake.set_max_width(w)


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
    foodPos = foodSp.spawn_food()
    snake.sences(foodPos)
    if snake.move(foodPos) == 1:
        score += 1
        print('score:  ', score)
        foodSp.set_food_on_screen(False)

    window.fill(pygame.Color(255, 255, 255))
    for pos in snake.get_body():
        pygame.draw.rect(window, pygame.Color(0, 200, 0), pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(window, pygame.Color(255, 0, 0), pygame.Rect(foodPos[0], foodPos[1], 10, 10))
    if snake.check_collision() == 1:
        gameOver()
    pygame.display.set_caption('wow snake | score: ' + str(score))
    pygame.display.flip()
    fps.tick(30)
