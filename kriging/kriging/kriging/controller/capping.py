# -*- coding: utf-8 -*-
class Capping:

    def __init__(self, minimum=None, maximum=None):
        self.minimum = minimum
        self.maximum = maximum

    def apply(self, value):
        if value < self.minimum:
            return self.minimum
        if value > self.maximum:
            return self.maximum