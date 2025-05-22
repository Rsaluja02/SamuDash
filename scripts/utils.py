import os

import pygame

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    img.set_colorkey((0, 0, 0))
    return img


def load_image_player(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    img = pygame.transform.scale_by(img, 0.32)
    return img


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def load_images_player(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image_player(path + '/' + img_name))
    return images




class Animation:
    def __init__(self, images, dur = 5,  loop = True):
        self.images = images
        self.loop = loop
        self.dur = dur
        self.done = False
        self.frame = 0
        
        
    def copy (self):
        return Animation(self.images , self.dur , self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.dur * len(self.images))
            
        else:
            self.frame = min(self.frame + 1 , self.dur * len(self.images) - 1)
            if self.frame >= self.dur * len(self.images) -1 :
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.dur)]