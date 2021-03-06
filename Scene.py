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

        self.easterEgg = False

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

        self.bottomObjectGroup = pygame.sprite.Group()
        self.middleObjectGroup = pygame.sprite.Group()
        self.topObjectGroup = pygame.sprite.Group()

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

        self.bottomObjectGroup.draw(screen)
        self.middleObjectGroup.draw(screen)
        self.topObjectGroup.draw(screen)

        self.ground.draw(screen)
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
        self.bottomObjectGroup.add(self.ground)
    
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

        self.bottomObjectGroup = pygame.sprite.Group()
        self.middleObjectGroup = pygame.sprite.Group()
        self.topObjectGroup = pygame.sprite.Group()

        self.hailGroup = pygame.sprite.Group()
        self.hailPool = HailPool(self, self.hailGroup)

        self.damageGroup = pygame.sprite.Group()

        self.updraft = Updraft(self.hailGroup)

        self.curSummonDelay = 0
        self.maxSummonDelay = 0.6

        self.easterEggCommand = "KNMTGCKLE"
        self.curEasterEggCommand = ""

        self.loadBackground()
        self.loadMap()

    def Update(self, deltaTime):
        self.updraft.update(deltaTime)
        self.hailGroup.update(deltaTime)
        self.UIGroup.update(deltaTime)
        self.damageGroup.update(deltaTime)

        self.bottomObjectGroup.update(deltaTime)
        self.middleObjectGroup.update(deltaTime)
        self.topObjectGroup.update(deltaTime)

        self.curSummonDelay += deltaTime

        self.summonHail()
        
        self.summonObjects()

    def ProcessInput(self, events, pressed_keys, deltaTime):
        self.updraft.processInput(events, pressed_keys, deltaTime)

        for event in events:
            if (event.type == pygame.KEYDOWN):
                self.curEasterEggCommand += event.unicode

                if (len(self.curEasterEggCommand) > len(self.easterEggCommand)):
                    self.curEasterEggCommand = self.curEasterEggCommand[1:]

                if (encrypt(b"easterEgg", self.curEasterEggCommand.encode()) == self.easterEggCommand.encode()):
                    self.easterEgg = not self.easterEgg
                    self.summonAing()

    def Render(self, screen):
        self.backgroundGroup.draw(screen)

        self.hailGroup.draw(screen)

        self.bottomObjectGroup.draw(screen)
        self.middleObjectGroup.draw(screen)
        self.topObjectGroup.draw(screen)

        self.damageGroup.draw(screen)
        self.ground.draw(screen)
        self.UIGroup.draw(screen)

        self.updraft.draw(screen)
    
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
        self.bottomObjectGroup.add(self.ground)

        self.summonObjects()
    
    def summonObjects(self):
        if (len(self.bottomObjectGroup) == 1):
            for i in range(1, 6):
                obj = random.choice([Building(self), House(self)])

                obj.Bottom = self.ground.Top
                obj.Position = i*self.width/6, obj.Position.y

                self.bottomObjectGroup.add(obj)

        if (len(self.middleObjectGroup) + len(self.topObjectGroup) == 0):
            for i in range(2):
                direction = random.choice(("left", "right"))
                speed = randint(3, 6)
                airplane = Airplane(self, direction, speed)
                airplane.Position = 0, self.height/9*(4+i)
                if (direction == "left"):
                    airplane.Right = 0
                else:
                    airplane.Left = self.width

                self.middleObjectGroup.add(airplane)
        
            direction = random.choice(("left", "right"))
            speed = randint(2, 5)
            satellite = Satellite(self, direction, speed)
            satellite.Position = 0, self.height/9
            if (direction == "left"):
                    satellite.Right = 0
            else:
                satellite.Left = self.width
            
            self.topObjectGroup.add(satellite)

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
    
    def summonAing(self):
        for i in range(0, self.height, 80):
            aing = Aing(self, 1, random.uniform(50, 60))
            aing.Position = Vector2(0, i)
            aing.Right = 0

            self.damageGroup.add(aing)

            aing = Aing(self, -1, random.uniform(50, 60))
            aing.Position = Vector2(0, i)
            aing.Left = self.width

            self.damageGroup.add(aing)
    

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

def encrypt(key : bytes, content : bytes):
    content = bytearray(content)
    for i in range(len(key)-1):
        for j in range(len(content)):
            content[j] = content[j] ^ key[i] ^ (key[i] | key[i+1])
    return bytes(content)