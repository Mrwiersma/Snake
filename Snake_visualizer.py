import pygame


class GeneralVisualiser:
    def __init__(self, window, origin=(0, 0)):
        self.window = window
        self.origin = origin
        pygame.font.init()
        font_type = pygame.font.get_default_font()
        self.text_size = 15
        self.font = pygame.font.Font(font_type, self.text_size)

    def show_general_info(self, gen, offset=(0, 0)):
        generation = self.font.render("Generation: {}".format(gen), True, (0, 0, 0))
        self.window.blit(generation, (self.origin[0] + offset[0], self.origin[1] + offset[1]))


class SnakeVisualizer:
    def __init__(self, obj, window, origin=(0, 0), size=(150, 200)):
        self.snake = obj
        self.window = window
        self.origin = origin
        self.size = size
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.ORANGE = (250, 118, 20)
        self.GREEN = (0, 255, 0)
        self.BLACK = (43, 43, 43)
        self.BACKGROUND = (200, 200, 200)
        pygame.font.init()
        font_type = pygame.font.get_default_font()
        self.text_size = 15
        self.font = pygame.font.Font(font_type, self.text_size)

    def clear_area(self):
        pygame.draw.rect(self.window, self.BACKGROUND, pygame.Rect(self.origin[0] - 10, self.origin[1] - 10, self.size[0], self.size[1]))

    def show_snake(self):
        self.clear_area()
        for pos in self.snake.get_body():
            pygame.draw.rect(self.window, self.GREEN, pygame.Rect(pos[0] + self.origin[0], pos[1] + self.origin[1], 10, 10))

        for pos in self.snake.get_walls():
            pygame.draw.rect(self.window, self.BLACK, pygame.Rect(pos[0] + self.origin[0], pos[1] + self.origin[1], 10, 10))

        pygame.draw.rect(self.window, self.RED,
                         pygame.Rect(self.snake.foodLoc[0] + self.origin[0], self.snake.foodLoc[1] + self.origin[1], 10, 10))

    def show_snake_vision(self):
        for pos in self.snake.get_vision():
            pygame.draw.rect(self.window, self.ORANGE, pygame.Rect(pos[0] + self.origin[0], pos[1] + self.origin[1], 10, 10))
        head = self.snake.get_head_pos()
        food = self.snake.get_food_pos()
        start = (head[0] + self.origin[0] + 5, head[1] + self.origin[1] + 5)
        end = (food[0] + self.origin[0] + 5, food[1] + self.origin[1] + 5)
        pygame.draw.line(self.window, self.ORANGE, start, end, 2)

    def show_info(self):
        snake_id = self.font.render("Snake_ID: {}".format(self.snake.ID), True, (0, 0, 0))
        snake_time_to_live = self.font.render("Time to live: {}".format(self.snake.time_to_live), True, (0, 0, 0))
        snake_fitness = self.font.render("Fitness: {}".format(self.snake.global_fitness), True, (0, 0, 0))
        food_loc = self.snake.food_quadrant
        if food_loc[1] == 1:
            food_n_s = "N"
        else:
            food_n_s = "S"
        if food_loc[0] == 1:
            food_e_w = "W"
        else:
            food_e_w = "E"
        snake_food_loc = self.font.render("Food location : [{}/{}]".format(food_n_s, food_e_w), True, (0, 0, 0))

        snake_window_height = self.snake.MaxHeight
        off_set = 15
        self.window.blit(snake_id, (self.origin[0] - 10, self.origin[1] + snake_window_height + off_set))
        self.window.blit(snake_time_to_live, (self.origin[0] - 10, self.origin[1] + snake_window_height + off_set + self.text_size))
        self.window.blit(snake_fitness, (self.origin[0] - 10, self.origin[1] + snake_window_height + off_set + self.text_size * 2))
        self.window.blit(snake_food_loc, (self.origin[0] - 10, self.origin[1] + snake_window_height + off_set + self.text_size * 3))


class NeuralNetVisualizer:
    def __init__(self, window, origin=(0, 0)):
        self.window = window
        self.origin = origin

    def show_neural_net(self, animated=False, origin=(0, 0)):
        pass
