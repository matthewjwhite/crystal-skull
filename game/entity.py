''' Contains common code across all entities '''

import random

class Entity:
    ''' Defines an entity '''

    #pylint: disable=unused-argument
    def __init__(self, name, health=100, strength=10, **kwargs):
        # **kwargs required as DB stores extra fields.
        self.name = name
        self.health = health
        self.strength = strength

    def lose(self, amount):
        ''' Subtracts an amount from health '''

        self.health = self.health - amount

    def hit(self):
        ''' Determines amount to hit '''

        return random.randrange(self.strength/2, self.strength)
