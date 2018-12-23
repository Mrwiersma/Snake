import random
import torch


class NaturalSelection:
    def __init__(self):
        self.mutate_chance = 10
        self.mutate_impact = 0.01
        self.current_population = {}
        self.new_population = {}
        self.elite = {}
        self.high_score = 0

        self.new_population_weights = {}
        self.children_weights = {}
        self.elite_weights = {}

        self.obj = classmethod
        self.width = 0
        self.height = 0

    def generate_first_pop(self, num, obj, w, h):
        for i in range(0, num):
            self.current_population[i] = {"Object": obj(i, 0, w, h), "Gen": 0, "ID": i, "Fitness": 0}
        self.update_pop_dict()
        self.width = w
        self.height = h
        self.obj = obj

    def update_pop_dict(self):
        for item in self.current_population:
            self.current_population[item]["Fitness"] = self.current_population[item]["Object"].global_fitness
            #print("fitness",self.current_population[item]["Object"].fitness)

    def select_elite(self, amount=20):
        self.update_pop_dict()
        temp = []
        for item in self.current_population:
            temp.append([item, self.current_population[item]["Fitness"]])
        temp.sort(key=lambda x: int(x[1]), reverse=True)
        self.high_score = temp[0][1]
        for i in range(0, amount):
            self.elite[i] = self.current_population[temp[i][0]]
            self.elite_weights[i] = self.current_population[temp[i][0]]["Object"].brain.get_weights()

    def breed(self, gen, p1, p2):
        self.update_pop_dict()
        par1 = torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(gen, p1))
        par2 = torch.load('NeuralNet/Models/Gen_{}/Snake_{}.pt'.format(gen, p2))
        child1 = par1
        child2 = par2

        for item in par1:  # iterate through keys
            temp1 = par1[item]

            for i in range(0, len(temp1)):
                if len(temp1[i].size()) == 0:
                    choice = random.choice([par1[item][i], par2[item][i]])
                    if choice == par1[item][i]:
                        child1[item][i] = self.mutate(choice)
                        child2[item][i] = self.mutate(par2[item][i])
                    else:
                        child1[item][i] = self.mutate(par1[item][i])
                        child2[item][i] = self.mutate(choice)
                else:
                    for j in range(0, len(temp1[i])):
                        choice = random.choice([par1[item][i][j], par2[item][i][j]])
                        if choice == par1[item][i][j]:
                            child1[item][i][j] = self.mutate(choice)
                            child2[item][i][j] = self.mutate(par2[item][i][j])
                        else:
                            child1[item][i][j] = self.mutate(par1[item][i][j])
                            child2[item][i][j] = self.mutate(choice)
        self.children_weights[len(self.children_weights)] = child1
        self.children_weights[len(self.children_weights)] = child2

    def mutate(self, x):
        if random.random() < self.mutate_chance:
            return x + random.uniform(-self.mutate_impact, self.mutate_impact)

    def create_new_population(self, children, elite, gen):
        self.new_population_weights = {}
        self.new_population = {}

        for i in range(0, children):
            parent1 = random.randint(0, len(self.current_population) - 1)
            parent2 = random.randint(0, len(self.current_population) - 1)
            while parent2 == parent1:
                parent2 = random.randint(0, len(self.current_population) - 1)
            self.breed(gen - 1, parent1, parent2)

        self.select_elite(elite)

        for i in range(0, len(self.elite)):
            self.children_weights[len(self.children_weights)] = self.elite_weights[i]

        self.new_population_weights = self.children_weights
        self.children_weights = {}
        self.new_population = {}
        for i in range(0, len(self.new_population_weights)):
            self.new_population[i] = {"Object": self.obj(i, gen, self.width, self.height), "Gen": gen, "ID": i, "Fitness": 0}
            self.new_population[i]["Object"].brain.set_weights(self.new_population_weights[i])
        self.update_pop_dict()
        self.current_population = self.new_population
