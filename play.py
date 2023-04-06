import pygame
from factory import FactoryEnv, FactoryAction
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    
    factory = FactoryEnv(asset_path='assets')
    reward_font = pygame.font.SysFont("monospace", 15)
    total_reward = 0.0
    info = {}
    while True:
        reward = 0.0
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    _, reward, _, info = factory.step(2)
                elif event.key == pygame.K_s:
                    _, reward, _, info = factory.step(FactoryAction.MOVE_CURSOR_DOWN)
                elif event.key == pygame.K_d:
                    _, reward, _, info = factory.step(FactoryAction.MOVE_CURSOR_RIGHT)
                elif event.key == pygame.K_a:
                    _, reward, _, info = factory.step(FactoryAction.MOVE_CURSOR_LEFT)
                elif event.key == pygame.K_1:
                    _, reward, _, info = factory.step(FactoryAction.BUILD_LEFT_BELT)
                elif event.key == pygame.K_2:
                    _, reward, _, info = factory.step(FactoryAction.BUILD_RIGHT_BELT)
                elif event.key == pygame.K_3:
                    _, reward, _, info = factory.step(FactoryAction.BUILD_UP_BELT)
                elif event.key == pygame.K_4:
                    _, reward, _, info = factory.step(FactoryAction.BUILD_DOWN_BELT)
                elif event.key == pygame.K_5:
                    _, reward, _, info = factory.step(FactoryAction.BUILD_MINE)
                elif event.key == pygame.K_6:
                    _, reward, _, info = factory.step(FactoryAction.BUILD_FURNACE)
                elif event.key == pygame.K_7:
                    _, reward, _, info = factory.step(FactoryAction.BUILD_PAPERCLIP_MACHINE)
                elif event.key == pygame.K_8:
                    _, reward, _, info = factory.step(FactoryAction.DESTROY_EQUIPMENT)
                elif event.key == pygame.K_q:
                    sys.exit()
                elif event.key == pygame.K_r:
                    factory.reset()
                    total_reward = 0.0
                print(info)
            elif event.type == pygame.QUIT:
                sys.exit()

        total_reward += reward
        map = factory.render()
        screen.blit(pygame.surfarray.make_surface(map), (0, 0))
        screen.blit(reward_font.render(f"reward: {total_reward:.2f}", 1, (0, 0, 0)), (10, 10))
        pygame.display.flip()

if __name__ == "__main__":
    main()
