import pygame
import sys
import random
import math
import os


from scripts.utils import load_image, load_images, Animation, load_image_player, load_images_player
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.sparks import Spark


def main():
    opening_game = True
    if opening_game:
        Game().run()


# Function For Background Track



class Game:
    def __init__(self):
        pygame.init()
        
        pygame.display.set_caption("SamuDash")

        # Create game window
        WIDTH = 800
        HEIGHT = 600
        WIDTH_d = WIDTH / 2
        HEIGHT_d = HEIGHT / 2
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.display = pygame.Surface((WIDTH_d, HEIGHT_d) , pygame.SRCALPHA)
        self.display_2 = pygame.Surface((WIDTH_d , HEIGHT_d))

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image_player('entities/player.png'),
            "background": load_image('orig.png'),
            "clouds": load_images("clouds"),
            "enemy/idle": Animation(load_images('entities/enemy/idle'), dur=6),
            "enemy/run": Animation(load_images('entities/enemy/run'), dur=4),
            "player/idle": Animation(load_images_player('entities/player/idle'), dur=6),
            "player/run": Animation(load_images_player('entities/player/run'), dur=4),
            "player/Jump": Animation(load_images_player('entities/player/Jump')),
            "player/slide": Animation(load_images_player('entities/player/slide')),
            "player/wall_slide": Animation(load_images_player("entities/player/wall_slide")),
            "particle/leaf": Animation(load_images('particles/leaf'), dur=20, loop=False),
            "particle/particle": Animation(load_images('particles/particle'), dur=6, loop=False),
            "gun": load_image("gun.png"),
            "projectile": load_image('projectile.png'),
            "icon": load_image('icon.png')

        }
        
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav')
        }


        pygame.display.set_icon(self.assets['icon'])

        self.sfx['ambience'].set_volume(0.3)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.6)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.5)
        
        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 17))

        self.tilemap = Tilemap(self, tile_size=16)
        self.level = 0
        self.load_level(self.level)
        self.screenshake = 0
        
    def bg_playsound(self):
            try:
                pygame.mixer.music.load("data/music.wav")
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1)
                self.sfx['ambience'].play(-1)
            except:
                sys.exit()

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawner = []

        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawner.append(pygame.Rect(
                4 + tree['pos'][0], 4+tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        self.projectiles = []
        self.particles = []
        self.scroll = [0, 0]
        self.sparks = []
        self.dead = 0
        self.transition = -30

# Background SOund
    def run(self):
        self.bg_playsound()
        while True:
            
            # Background Render
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) -1 )
                    self.load_level(self.level)
            if self.transition < 0: 
                self.transition += 1


            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)

# Camera positining offset
            self.scroll[0] += (self.player.rect().centerx -
                               self.display.get_width()/2 - self.scroll[0])/30
            self.scroll[1] += (self.player.rect().centery -
                               self.display.get_height()/2 - self.scroll[1])/30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

# leaf particle Spawner and Control
            for rect in self.leaf_spawner:
                if random.random() * 35000 < rect.width * rect.height:
                    pos = (rect.x + random.random()*rect.width,
                           rect.y + random.random() * rect.height)
                    self.particles.append(
                        Particle(self, 'leaf', pos, velocity=[0.1, 0.3], frame=random.randint(0, 20)))

# CLoud Render
            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

# Map Render
            self.tilemap.render(self.display, offset=render_scroll)

# Enemy Render
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
# player render
            if not self.dead:
                self.player.update(
                    self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets["projectile"]
                self.display.blit(img, (projectile[0][0] - img.get_width(
                ) / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random(
                        ) - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(
                                Spark(self.player.rect().center, angle, 2+random.random()))
                            self.particles.append(Particle(self, "particle", self.player.rect().center, velocity=[math.cos(
                                angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1,0) , (1,0) , (0,-1) , (-1,0)]:
                self.display_2.blit(display_sillhouette , offset)

# leaf particle render
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.p_type == "leaf":
                    # To produce Wavey effect for falling of leaves
                    particle.pos[0] += math.sin(
                        particle.animation.frame * 0.033) * 0.3
                if kill:
                    self.particles.remove(particle)

# Movenment and Controls
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False


# Level Change Transition
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255,255,255) , (self.display.get_width() // 2 , self.display.get_height() // 2) , (30  -abs(self.transition)) * 8)
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf , (0,0))
                


# GameScreen Render

            self.display_2.blit(self.display, (0,0))
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                  random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(
                self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()

# Clock Object for timing game/FPS
            self.clock.tick(60)


main()
