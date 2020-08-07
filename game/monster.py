''' Contains code related to monsters '''

import random

class Monster():
    ''' Monster '''

    def __init__(self, name, health, strength):
        self.name = name
        self.health = health
        self.strength = strength

    def lose(self, amount):
        ''' Subtracts an amount from health '''

        self.health = self.health - amount

    def hit(self):
        ''' Determines amount to hit '''

        return random.randint(self.strength/2, self.strength)
