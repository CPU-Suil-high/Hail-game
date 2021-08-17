import pygame
import Scene
from pypresence import Presence
import time

from Sprites import Text

WIDTH = 500
HEIGHT = 700

def main(fps, starting_scene):
    global screen

    clock = pygame.time.Clock()
    fpsVisible = False

    active_scene = starting_scene
    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        deltaTime = clock.tick(fps) / 100

        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False # 게임 종료 여부
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
                elif event.key == pygame.K_f:
                    fpsVisible = not fpsVisible

            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys, deltaTime)
        active_scene.Update(deltaTime)
        active_scene.Render(screen)

        active_scene = active_scene.next

        if (fpsVisible):
            fpsImage = pygame.font.SysFont("Arial", 24).render(str(int(clock.get_fps())), 1, (255, 0, 0))
            screen.blit(fpsImage, (0,0))

        pygame.display.flip()
    pygame.quit()

def connect_discord():
    global RPC
    RPC = Presence(875405629651582976)
    RPC.connect()

    start_time = time.time()

    RPC.update(large_image="title", large_text="Hail", start=start_time)

def setPygame():
    pygame.display.set_caption("Hail")
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

    surface = pygame.Surface((100, 100))
    surface.fill((0,0,0))

    text = Text("Hail", pygame.font.SysFont("Impact", 60), (255, 255, 255))
    text.Position = (surface.get_width()/2, surface.get_height()/2)

    text.draw(surface)

    pygame.display.set_icon(surface)

if (__name__ == "__main__"):
    global RPC
    connect_discord()

    pygame.init()

    setPygame()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    main(300, Scene.StartScene(WIDTH, HEIGHT))
    
    RPC.close()