# -*- coding: utf-8 -*-
class Polylines:

    def __init__(self, polylines):
        self.polylines = polylines

    def __iter__(self):
        return iter(self.polylines)

    def __len__(self):
        return len(self.polylines)

    def __getitem__(self, i):
        return self.polylines[i]