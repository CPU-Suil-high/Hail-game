import pygame
from pygame.math import Vector2
from queue import Queue

from Sprites import Hail

class HailPool:
    def __init__(self, scene, hailGroup):
        self.scene = scene
        self.hailGroup = hailGroup
        self.pool = Queue()
    
    def summonHail(self, radius=1):
        if (self.pool.empty()):
            return Hail(self.scene, radius)
        else:
            hail = self.pool.get()
            hail.Position = (0,0)
            hail.velocity = (0,0)
            hail.radius = radius
            hail.loadImage()
            hail.bounceCount = 0

            return hail
    
    def returnHail(self, hail):
        self.hailGroup.remove(hail)
        self.pool.put(hail)