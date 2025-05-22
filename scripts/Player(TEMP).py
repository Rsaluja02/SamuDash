import pygame
from os.path import isfile,join
from os import listdir

class Player1:
    def __init__(self, dir1, dir2, width, height, direction):
        
        self.dir1 = dir1
        self.dir2 = dir2
        self.width = width
        self.height = height
        self.direction = direction
    

    def flip(self, sprites):
        return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


    def load_sprite_sheet(self):
        path = join("data" , self.dir1 , self.dir2)
        images = [f for f in listdir(path) if isfile(join(path, f))]
        
        all_sprites = {}
        
        for image in images:
            sprite_sheet = pygame.image.load(join(path , image)).convert_alpha()
            
            sprites = []
            for i in range(sprite_sheet.get_width() // self.width):
                surface = pygame.surface((self.width, self.height) , pygame.SRCALPHA , 32)
                
                rect = pygame.rect(i * self.width, 0 , self.width , self.height)
                surface.blit(sprite_sheet, (0,0) , rect)
                
                sprites.append(pygame.transform.scale2x(surface))
                
                
            if self.direction:
                all_sprites[image.replace(".png" , "")+ '_right'] = sprites
                all_sprites[image.replace(".png" , "")+ '_left'] = self.flip(sprites)
            else:
                all_sprites[image.replace('.png', "")] = sprites
                
        return all_sprites
                
            
            
