import pygame
from pygame import Vector2, Vector3, gfxdraw
from copy import deepcopy

from random import randint

G = 1 # 중력가속도

class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, size=(0,0)):
        super().__init__()
        self.position = Vector2()
        self.image = pygame.Surface(size)
        self.rect = pygame.Rect((0, 0), size)
        self.loadImage()
        self.rect.center = (0, 0)

    @property
    def Position(self):
        return deepcopy(self.position)
    @Position.setter
    def Position(self, position):
        self.position = Vector2(position)
        self.rect.center = position
    
    @property
    def Rect(self):
        return deepcopy(self.rect)

    @property
    def Center(self):
        return self.rect.center
    @Center.setter
    def Center(self, position):
        self.rect.center = position
        self.Position = self.rect.center
    
    @property
    def Top(self):
        return self.rect.top
    @Top.setter
    def Top(self, position):
        self.rect.top = position
        self.Position = self.rect.center

    @property
    def Bottom(self):
        return self.rect.bottom
    @Bottom.setter
    def Bottom(self, position):
        self.rect.bottom = position
        self.Position = self.rect.center
    
    @property
    def Right(self):
        return self.rect.right
    @Right.setter
    def Right(self, position):
        self.rect.right = position
        self.Position = self.rect.center

    @property
    def Left(self):
        return self.rect.left
    @Left.setter
    def Left(self, position):
        self.rect.left = position
        self.Position = self.rect.center

    @property
    def Image(self):
        return self.image
    @Image.setter
    def Image(self, image):
        self.image = image
        self.rect = self.image.get_rect(center=self.Position)
        
    def loadImage(self):
        pass
    
    def update(self, deltaTime):
        pass

    def processInput(self, events, pressed_keys, deltaTime):
        pass
    
    def draw(self, screen):
        screen.blit(self.Image, self.Rect)

class Hail(BaseSprite):
    def __init__(self, scene, radius=1):
        self.radius = radius
        self.growSpeed = 0.06
        self.bonusGrowSpeed = 0.08
        self.mess = self.radius**2 / 10 + 2
        self.velocity = Vector2()
        self.maxVelocity = 100
        self.bounceCount = 0
        self.maxBounceCount = 3

        self.scene = scene
        super().__init__(size=(0,0))
    
    def update(self, deltaTime):
        if (self.Bottom < 0):
            self.radius += deltaTime * self.bonusGrowSpeed
        else:
            self.radius += deltaTime * self.growSpeed
        self.mess = self.radius**2 / 40 + 2
        self.loadImage()
        self.calculatePhysics(deltaTime)
        self.collision(deltaTime)
    
    def calculatePhysics(self, deltaTime):
        self.velocity.y += G * deltaTime

        if (self.velocity.length() > self.maxVelocity):
            self.velocity.scale_to_length(self.maxVelocity)
        self.Position += self.velocity * deltaTime

        if (self.Top > self.scene.height):
            self.kill()
        elif (self.Left > self.scene.width):
            self.Right = 0
        elif (self.Right < 0):
            self.Left = self.scene.width
    
    def addForce(self, force):
        self.velocity += force / self.mess

    def collision(self, deltaTime):
        if (self.Position.y < 0):
            return
        elif (self.Position.y <= self.scene.height/3):
            group = self.scene.topObjectGroup
        elif (self.Position.y <= self.scene.height/3*2):
            group = self.scene.middleObjectGroup
        else:
            group = self.scene.bottomObjectGroup

        for sprite in group:
            if (sprite.state == "fadeIn"):
                continue
            if (not pygame.sprite.collide_rect(self, sprite)):
                continue

            if (pygame.sprite.collide_mask(self, sprite)):
                self.Position -= self.velocity * deltaTime

                if (self.radius >= 5):
                    damageValue = int(self.radius**2/5)
                    sprite.takeDamage(damageValue, self.Position)

                if (self.Position.x > sprite.Right):
                    vec1 = Vector2(40, randint(-50, 50))
                    vec2 = Vector2(40, randint(-50, 50))
                elif (self.Position.x < sprite.Left):
                    vec1 = Vector2(-40, randint(-50, 50))
                    vec2 = Vector2(-40, randint(-50, 50))
                elif (self.Position.y > sprite.Center[1]):
                    vec1 = Vector2(randint(-50, 50), 40)
                    vec2 = Vector2(randint(-50, 50), 40)
                elif (self.Position.y < sprite.Center[1]):
                    vec1 = Vector2(randint(-50, 50), -40)
                    vec2 = Vector2(randint(-50, 50), -40)

                if (self.radius < 7):
                    if (self.bounceCount > self.maxBounceCount):
                        self.scene.hailPool.returnHail(self)
                    else:
                        vec1.scale_to_length(self.velocity.length()/4)
                        self.velocity = vec1
                        self.radius = max(self.radius*3/4, 1)
                        self.bounceCount += 1
                else:
                    hail1 = Hail(self.scene, self.radius/2)
                    hail1.Position = self.Position
                    vec1.scale_to_length(10)
                    hail1.velocity = vec1

                    hail2 = Hail(self.scene, self.radius/2)
                    hail2.Position = self.Position
                    vec2.scale_to_length(10)
                    hail2.velocity = vec2
                    
                    self.scene.hailGroup.add(hail1, hail2)

                    self.scene.hailPool.returnHail(self)

    def loadImage(self):
        image = pygame.Surface((self.radius*2+1, self.radius*2+1), pygame.SRCALPHA, 32)

        gfxdraw.aacircle(image, *(int(self.radius), int(self.radius)), int(self.radius), (255, 255, 255))
        gfxdraw.filled_circle(image, *(int(self.radius), int(self.radius)), int(self.radius), (255, 255, 255))
        self.Image = image

class Updraft(BaseSprite):
    def __init__(self, hailGroup):
        super().__init__()
        self.hailGroup = hailGroup
        self.Position = Vector2(-100, -100)
        self.power = 350
        self.leftClick = False

    def update(self, deltaTime):
        if (self.leftClick):
            self.Position = Vector2(pygame.mouse.get_pos()) - Vector2(0, self.Rect.height/5)
        for hail in self.hailGroup:
            if (pygame.sprite.collide_rect(self, hail)):
                direction = (hail.Position - self.Position - Vector2(0, self.Rect.height/5))
                distance = direction.length()
                direction.normalize_ip()
                if (distance < 1):
                    force = direction * self.power * deltaTime
                else:
                    force = direction * (self.power / distance) * deltaTime
                hail.addForce(force)

    def processInput(self, events, pressed_keys, deltaTime):
        for event in events:
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == pygame.BUTTON_LEFT):
                    self.leftClick = True
            elif (event.type == pygame.MOUSEBUTTONUP):
                if (event.button == pygame.BUTTON_LEFT):
                    self.leftClick = False
                    self.Right = -1000

    def loadImage(self):
        image = pygame.Surface((100,125), pygame.SRCALPHA, 32)
        image.set_alpha(100)
        image.fill((0,255,0, 100))
        self.Image = image

class BaseObject(BaseSprite):
    def __init__(self, maxHp, score, scene, fadeTime, fallingSpeed):
        self.hp = maxHp
        self.maxHp = maxHp
        self.score = score
        self.scene = scene
        self.state = "fadeOut"
        self.maxFadeTime = fadeTime
        self.curFadeTime = 0
        self.fallingSpeed = fallingSpeed
        super().__init__()
    
    def update(self, deltaTime):
        if (self.state == "normal"):
            return
        elif (self.state == "fadeOut"):

            self.curFadeTime += deltaTime / 10

            if (self.curFadeTime >= self.maxFadeTime):
                self.state = "normal"
                self.curFadeTime = self.maxFadeTime
        elif (self.state == "fadeIn"):

            self.curFadeTime -= deltaTime / 10

            if (self.curFadeTime <= 0):
                super().kill()

            self.Position += Vector2(0, deltaTime*self.fallingSpeed)
        
        alpha = self.curFadeTime/self.maxFadeTime*255
        self.image.set_alpha(alpha)

    def loadImage(self):
        alpha = self.curFadeTime/self.maxFadeTime*255
        self.image.set_alpha(alpha)

    def kill(self):
        self.scene.score.scoreValue += self.score
        self.remove()
        self.state = "fadeIn"
    
    @property
    def HP(self):
        return self.hp
    @HP.setter
    def HP(self, hp):
        if (hp < 0):
            self.kill()
        else:
            self.hp = hp
    
    def takeDamage(self, damageValue, position):
        self.HP -= damageValue
        damage = Damage(damageValue)
        damage.Position = position
        self.scene.damageGroup.add(damage)

class Ground(BaseObject):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        super().__init__(0, 0, None, 0, 0)

    @property
    def HP(self):
        return self.hp
    @HP.setter
    def HP(self, hp):
        self.hp = 0
    
    def update(self, deltaTime):
        pass
    
    def loadImage(self):
        image = pygame.Surface((self.width*2, 30))
        image.fill((52, 201, 90))
        self.Image = image
    
    def takeDamage(self, damageValue, position):
        pass

class Building(BaseObject):
    def __init__(self, scene):
        maxHp = 80
        score = 3
        fadeTime = 1
        fallingSpeed = 4
        super().__init__(maxHp, score, scene, fadeTime, fallingSpeed)
    
    def loadImage(self):
        image = pygame.Surface((50, 100), pygame.SRCALPHA, 32)

        image.fill((105, 105, 105))

        window = pygame.Surface((10, 10))
        window.fill((0, 131, 179))

        for i in range(4):
            for j in range(2):
                image.blit(window, (10+j*20, 10+i*20))

        self.Image = image

        super().loadImage()

class House(BaseObject):
    def __init__(self, scene):
        maxHp = 50
        score = 2
        fadeTime = 1
        fallingSpeed = 3
        super().__init__(maxHp, score, scene, fadeTime, fallingSpeed)
    
    def loadImage(self):
        image = pygame.Surface((50, 50), pygame.SRCALPHA, 32)

        image.fill((148, 101, 0), (5, 25, 40, 50))
        
        pygame.draw.polygon(image, (148, 101, 0), [(0, 25), (24, 10), (49, 25)])
        pygame.draw.lines(image, (94, 64, 0), False, [(0, 25), (24, 10), (49, 25)], width=4)

        image.fill((94, 64, 0), (20, 30, 10, 20))
        image.fill((0,0,0), (26, 39, 2, 2))

        self.Image = image

        super().loadImage()

class Airplane(BaseObject):
    def __init__(self, scene, direction, speed):
        maxHp = 30
        score = 1
        fallingSpeed = 5

        self.speed = speed

        if (direction == "left"):
            self.direction = -1
        elif (direction == "right"):
            self.direction = 1

        super().__init__(maxHp, score, scene, 1, fallingSpeed)

    def update(self, deltaTime):
        super().update(deltaTime)
        self.Position += Vector2(self.speed*deltaTime*self.direction, 0)

        if (self.direction == 1 and self.Left > self.scene.width):
            self.Right = 0
        elif (self.direction == -1 and self.Right < 0):
            self.Left = self.scene.width
    
    def loadImage(self):
        image = pygame.Surface((50, 20), pygame.SRCALPHA, 32)
        image.fill((71, 142, 255))

        self.Image = image

        super().loadImage()

class Satellite(BaseObject):
    def __init__(self, scene, direction, speed):
        maxHp = 30
        score = 1
        fallingSpeed = 5

        self.speed = speed

        if (direction == "left"):
            self.direction = -1
        elif (direction == "right"):
            self.direction = 1

        super().__init__(maxHp, score, scene, 1, fallingSpeed)

    def update(self, deltaTime):
        super().update(deltaTime)
        self.Position += Vector2(self.speed*deltaTime*self.direction, 0)

        if (self.direction == 1 and self.Left > self.scene.width):
            self.Right = 0
        elif (self.direction == -1 and self.Right < 0):
            self.Left = self.scene.width
    
    def loadImage(self):
        image = pygame.Surface((50, 20), pygame.SRCALPHA, 32)
        image.fill((217, 159, 0))

        self.Image = image

        super().loadImage()

class Damage(BaseSprite):
    def __init__(self, damageValue):
        self.damageValue = damageValue
        self.maxKillDelay = 40
        self.curKillDelay = 0
        self.riseSpeed = 1
        super().__init__()
    
    def update(self, deltaTime):
        self.Position += Vector2(0, -self.riseSpeed*deltaTime)
        self.curKillDelay += deltaTime

        if (self.curKillDelay >= self.maxKillDelay):
            self.kill()
        
        alpha = ((self.maxKillDelay/2) - (self.curKillDelay - self.maxKillDelay/2)) / (self.maxKillDelay/2) * 255
        self.image.set_alpha(alpha)
    
    def loadImage(self):
        font = pygame.font.SysFont("Arial", 13)
        font.set_bold(True)
        image = font.render(str(self.damageValue), True, (255, 0, 0))

        self.Image = image

class Button(BaseSprite):
    def __init__(self, name, func):
        self.name = name
        self.func = func
        super().__init__()
    
    def processInput(self, events, pressed_keys, deltaTime):
        for event in events:
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == pygame.BUTTON_LEFT):
                    if (self.Rect.collidepoint(pygame.mouse.get_pos())):
                        self.click()
    
    def update(self, deltaTime):
        self.loadImage()
    
    def loadImage(self):
        image = pygame.Surface((150, 22))

        imageRect = image.get_rect()
        
        if (self.Rect.collidepoint(pygame.mouse.get_pos())):
            image.fill((65, 119, 156))
        else:
            image.fill((0, 41, 69))

        font = pygame.font.SysFont("Tahoma", 20)
        fontImage = font.render(self.name, True, (255, 255, 255))
        fontRect = fontImage.get_rect()
        fontRect.bottomleft = imageRect.bottomleft
        fontRect.left += 5

        image.blit(fontImage, fontRect)

        self.Image = image

    def click(self):
        self.func()

class Timer(BaseSprite):
    def __init__(self, endTime, func):
        self.active = True
        self.curTime = 0
        self.endTime = endTime
        self.func = func
        super().__init__()
    
    def update(self, deltaTime):
        self.curTime += deltaTime / 10
        if (self.endTime - self.curTime <= 0):
            if (self.active):
                self.func()
                self.active = False
        else:
            self.loadImage()
    
    def loadImage(self):
        second = round((self.endTime - self.curTime))
        minute = second // 60
        second = second % 60

        font = pygame.font.SysFont("Arial", 20)
        image = font.render(f"{minute:0>2}:{second:0>2}", True, (30,30,30))

        self.Image = image

class Background(BaseSprite):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        super().__init__()

    def loadImage(self):
        start = Vector3(0,0,0)
        end = Vector3(0, 136, 242)
        image = pygame.Surface((self.width, self.height))

        for y in range(self.height):
            color = start.lerp(end, y/(self.height-1))
            for x in range(self.width):
                image.set_at((x, y), color)
        
        self.Image = image

class FadeOut(Timer):
    def __init__(self, endTime, func, width, height):
        self.width = width
        self.height = height

        super().__init__(endTime, func)
    
    def update(self, deltaTime):
        super().update(deltaTime)
        if (self.curTime - self.endTime >= 0.5):
            self.kill()

    def loadImage(self):
        alpha = (self.curTime)/(self.endTime)*255
        image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        image.fill((0,0,0))

        image.set_alpha(alpha)

        self.Image = image

class FadeIn(Timer):
    def __init__(self, endTime, func, width, height):
        self.width = width
        self.height = height

        super().__init__(endTime, func)

    def update(self, deltaTime):
        super().update(deltaTime)
        if (self.curTime - self.endTime >= 0.5):
            self.kill()

    def loadImage(self):
        alpha = (self.endTime - self.curTime) / (self.endTime)*255
        image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        image.fill((0,0,0))

        image.set_alpha(alpha)

        self.Image = image

class Score(BaseSprite):
    def __init__(self, scoreValue=0, fontSize=20, color=(30, 30, 30)):
        self.scoreValue = scoreValue
        self.fontSize = fontSize
        self.color = color
        super().__init__()
    
    def update(self, deltaTime):
        self.loadImage()

    def loadImage(self):
        image = pygame.font.SysFont("Arial", self.fontSize).render(f"Score : {self.scoreValue:0>2}", True, self.color)

        self.Image = image

class Text(BaseSprite):
    def __init__(self, textValue, font, color=(0,0,0)):
        self.textValue = textValue
        self.font = font
        self.color = color
        super().__init__()
    
    def loadImage(self):
        image = self.font.render(self.textValue, True, self.color)

        self.Image = image