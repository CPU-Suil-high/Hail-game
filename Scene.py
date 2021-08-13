import pygame
from pygame import Vector2
from Sprites import *
from Pools import *
import random

class Scene:
    def __init__(self, width, height):
        self.next = self
        self.width = width
        self.height = height

        self.UIGroup = pygame.sprite.Group()

        self.loadUI()

        self.startPadeIn(1)

    def Update(self, deltaTime):
        print("No override")
    def ProcessInput(self, events, pressed_keys, deltaTime):
        print("No override")
    def Render(self, screen):
        print("No override")
    def SwitchToScene(self, next_scene, *args):
        self.startPadeOut(1, lambda : self.setNext(next_scene, args))
    def Terminate(self):
        self.SwitchToScene(None)
    def setNext(self, scene, args):
        if (scene == None):
            self.next = None
        else:
            self.next = scene(*args)

    def loadUI():
        pass
    
    def startPadeOut(self, time=1, func=lambda : None):
        fadeOut = FadeOut(time, func, self.width, self.height)
        fadeOut.Left = 0
        fadeOut.Top = 0

        self.UIGroup.add(fadeOut)
    
    def startPadeIn(self, time=1, func=lambda : None):
        fadeIn = FadeIn(time, func, self.width, self.height)
        fadeIn.Left = 0
        fadeIn.Top = 0

        self.UIGroup.add(fadeIn)

class StartScene(Scene):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.backgroundGroup = pygame.sprite.Group()

        self.mapGroup = pygame.sprite.Group()

        self.hailGroup = pygame.sprite.Group()
        self.hailPool = HailPool(self, self.hailGroup)

        self.curSummonDelay = 0
        self.maxSummonDelay = 2

        self.loadBackground()
        self.loadMap()
    
    def Update(self, deltaTime):
        self.hailGroup.update(deltaTime)
        self.UIGroup.update(deltaTime)

        self.curSummonDelay += deltaTime

        self.summonHail()
    
    def ProcessInput(self, events, pressed_keys, deltaTime):
        for i in self.UIGroup:
            i.processInput(events, pressed_keys, deltaTime)
    
    def Render(self, screen):
        self.backgroundGroup.draw(screen)
        self.hailGroup.draw(screen)
        self.mapGroup.draw(screen)
        self.UIGroup.draw(screen)
    
    def loadUI(self):
        startButton = Button("Start", lambda : self.SwitchToScene(GameScene, self.width, self.height))
        startButton.Position = (self.width/2, self.height/2)

        title = Text("Hail", pygame.font.SysFont("Impact", 70), (255, 255, 255))
        title.Position = (self.width/2, 0)
        title.Top = 50

        self.UIGroup.add(startButton, title)
    
    def loadMap(self):
        self.ground = Ground(self.width, self.height)
        self.ground.Position = (self.width/2, 0)
        self.ground.Bottom = self.height
        self.mapGroup.add(self.ground)
    
    def loadBackground(self):
        background = Background(self.width, self.height)
        background.Left = 0
        background.Top = 0

        self.backgroundGroup.add(background)
    
    def summonHail(self):
        if (self.curSummonDelay > self.maxSummonDelay):
            self.curSummonDelay -= self.maxSummonDelay

            hail = self.hailPool.summonHail()

            hail.Position = (random.randint(0, self.width), 0)

            hail.velocity = Vector2(0, 10)

            self.hailGroup.add(hail)

class GameScene(Scene):
    def __init__(self, width, height):
        self.timeLimit = 120

        super().__init__(width, height)

        self.backgroundGroup = pygame.sprite.Group()

        self.mapGroup = pygame.sprite.Group()

        self.hailGroup = pygame.sprite.Group()
        self.hailPool = HailPool(self, self.hailGroup)

        self.updraft = Updraft(self.hailGroup)

        self.curSummonDelay = 0
        self.maxSummonDelay = 0.8

        self.loadBackground()
        self.loadMap()

    def Update(self, deltaTime):
        self.updraft.update(deltaTime)
        self.hailGroup.update(deltaTime)
        self.UIGroup.update(deltaTime)
        self.mapGroup.update(deltaTime)

        self.curSummonDelay += deltaTime

        self.summonHail()
        
        if (len(self.mapGroup) < 2):
            self.summonObjects()

    def ProcessInput(self, events, pressed_keys, deltaTime):
        self.updraft.processInput(events, pressed_keys, deltaTime)

    def Render(self, screen):
        self.backgroundGroup.draw(screen)
        self.hailGroup.draw(screen)
        self.mapGroup.draw(screen)
        self.updraft.draw(screen)
        self.UIGroup.draw(screen)
    
    def loadUI(self):
        timer = Timer(self.timeLimit, lambda : self.SwitchToScene(EndScene, self.width, self.height, self.score.scoreValue))
        timer.Left = 5
        timer.Bottom = self.height - 5

        self.score = Score()
        self.score.Right = self.width - 5
        self.score.Bottom = self.height - 5

        self.UIGroup.add(timer, self.score)

    def loadMap(self):
        self.ground = Ground(self.width, self.height)
        self.ground.Position = (self.width/2, 0)
        self.ground.Bottom = self.height
        self.mapGroup.add(self.ground)

        self.summonObjects()
    
    def summonObjects(self):
        for i in range(1, 6):
            obj = random.choice([Building(self), House(self)])

            obj.Bottom = self.ground.Top
            obj.Position = i*self.width/6, obj.Position.y

            self.mapGroup.add(obj)

    def loadBackground(self):
        background = Background(self.width, self.height)
        background.Left = 0
        background.Top = 0

        self.backgroundGroup.add(background)
    
    def summonHail(self):
        if (self.curSummonDelay > self.maxSummonDelay):
            self.curSummonDelay -= self.maxSummonDelay

            hail = self.hailPool.summonHail()

            hail.Position = (random.randint(0, self.width), 0)

            hail.velocity = Vector2(0, 10)

            self.hailGroup.add(hail)
    

class EndScene(Scene):
    def __init__(self, width, height, scoreValue):
        self.scoreValue = scoreValue

        super().__init__(width, height)

        self.backgroundGroup = pygame.sprite.Group()

        self.loadBackground()

        self.startPadeIn()
    
    def Update(self, deltaTime):
        self.backgroundGroup.update(deltaTime)
        self.UIGroup.update(deltaTime)
    
    def ProcessInput(self, events, pressed_keys, deltaTime):
        for i in self.UIGroup:
            i.processInput(events, pressed_keys, deltaTime)
    
    def Render(self, screen):
        self.backgroundGroup.draw(screen)
        self.UIGroup.draw(screen)

    def loadBackground(self):
        background = Background(self.width, self.height)
        background.Left = 0
        background.Top = 0

        self.backgroundGroup.add(background)
    
    def loadUI(self):
        backButton = Button("Back", lambda : self.SwitchToScene(StartScene, self.width, self.height))

        backButton.Position = (self.width/2, self.height/4*3)

        self.score = Text(str(self.scoreValue), font=pygame.font.SysFont("Impact", 30), color=(0, 133, 77))

        self.score.Position = (self.width/2, self.height/8*3)

        self.scoreTitle = Text("Score", pygame.font.SysFont("Impact", 50), color=(0, 222, 129))

        self.scoreTitle.Position = (self.width/2, self.height/4)

        self.UIGroup.add(backButton, self.score, self.scoreTitle)