import random
import torch
import numpy as np


class NaturalSelection:
    def __init__(self, obj, w, h):
        self.high_score = 0
        self.current_gen = 0
        self.nn_layout = None

        self.mutating = True
        self.mutate_chance = 80
        self.mutate_impact = 0.1
        self.current_population = []
        self.new_population = []

        self.ranked_list = []

        self.new_population_weights = []
        self.children_weights = []
        self.elite_weights = []

        self.obj = obj
        self.width = w
        self.height = h

    def set_mutate_params(self, mutating=True, chance=10, impact=0.1):
        self.mutating = mutating  # of het uberhaupt muteerd
        self.mutate_chance = chance  # de kans dat er gemuteerd wordt
        self.mutate_impact = impact  # de maximale aanpassing (zowel + als -)

    def set_nn_layout(self, x):
        self.nn_layout = x

    def generate_first_population(self, amount):
        self.current_population = []
        self.current_gen = 0
        for i in range(0, amount):
            new_snake = self.obj(i, self.current_gen, self.width, self.height, network_layout=self.nn_layout)
            new_snake.brain.save_model(self.current_gen, i)
            self.current_population.append(new_snake)

    def ranking_list(self):  # maakt een lijst met [Snake.ID,Snake.global_Fitness] en sorteerd op fitnes (hoog naar laag)
        self.ranked_list = []
        for item in self.current_population:
            self.ranked_list.append([item.ID, item.global_fitness])

        self.ranked_list.sort(key=lambda x: int(x[1]), reverse=True)
        self.high_score = self.ranked_list[0]

    def update_elite_weights(self, num):  # slaat alleen de gewichten van de elite op
        self.ranking_list()
        print(self.ranked_list)
        self.elite_weights = []
        for item in self.ranked_list[:num]:
            self.elite_weights.append(torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(self.current_gen, item[0])))

    def breed(self, p1, p2):  # Kindjesssss
        par1 = torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(self.current_gen, p1))
        par2 = torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(self.current_gen, p2))
        child1 = torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(self.current_gen, p1))
        child2 = torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(self.current_gen, p1))

        for item in par1:  # Terror maar t werkt
            temp1 = par1[item]

            for i in range(0, len(temp1)):
                if len(temp1[i].size()) == 0:
                    choice = random.choice([par1[item][i], par2[item][i]])
                    if choice == par1[item][i]:
                        child1[item][i] = choice + self.mutate()  # voegt direct een mutatie toe (zie mutate)
                        child2[item][i] = par2[item][i] + self.mutate()
                    else:
                        child1[item][i] = par1[item][i] + self.mutate()
                        child2[item][i] = choice + self.mutate()
                else:
                    for j in range(0, len(temp1[i])):
                        choice = random.choice([par1[item][i][j], par2[item][i][j]])
                        if choice == par1[item][i][j]:
                            child1[item][i][j] = choice + self.mutate()
                            child2[item][i][j] = par2[item][i][j] + self.mutate()
                        else:
                            child1[item][i][j] = par1[item][i][j] + self.mutate()
                            child2[item][i][j] = choice + self.mutate()
        self.children_weights.append(child1)
        self.children_weights.append(child2)


    def mutate(self):
        if self.mutating:
            if random.uniform(0, 100) < self.mutate_chance:
                return random.uniform(-self.mutate_impact, self.mutate_impact)
            else:
                return 0
        else:
            return 0

    def select_parents(self, num_of_parents):
        self.ranking_list()
        parent_ids = []
        ids = np.random.geometric(0.1, num_of_parents)
        print(len(ids))
        for i in range(0, num_of_parents):
            parent_ids.append(self.ranked_list[ids[i]][0])

        return parent_ids

    def create_new_population(self, children, elite):  # dit werkt vgm, maakt nieuwe populatie en set de weights van het NN
        self.new_population_weights = []
        self.new_population = []
        self.children_weights = []
        print(" current gen", self.current_gen)

        parents = self.select_parents(children)
        print(len(parents))

        for i in range(0, children):
            parent1 = parents[i]
            parent2 = parents[-i]
            while parent2 == parent1:
                parent2 = random.choice(parents)
            self.breed(parent1, parent2)

        self.update_elite_weights(elite)

        self.new_population_weights = self.children_weights + self.elite_weights

        for i in range(0, len(self.new_population_weights)):
            new_snake = (self.obj(i, self.current_gen + 1, self.width, self.height, network_layout=self.nn_layout))
            new_snake.brain.set_weights(self.new_population_weights[i])
            new_snake.brain.save_model(self.current_gen + 1, i)  # hier wordt uiteindelijk de juiste set gewichten toegewezen
            self.new_population.append(new_snake)

        self.current_population = self.new_population
        self.current_gen += 1
        self.new_population = []
