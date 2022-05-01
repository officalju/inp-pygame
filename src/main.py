from ctypes.wintypes import RGB
from distutils.util import execute
from pickle import FALSE
from re import X
from turtle import width
import pygame



import sys



class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(Config.WHITE)
        return sprite



class Config:
    TILE_SIZE = 32
    WINDOW_WIDTH = TILE_SIZE * 20
    WINDOW_HEIGHT = TILE_SIZE * 10
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    GREY = (128, 128, 128)
    WHITE = (255, 255, 255)
    FPS = 25
    BG_SPEED = 1



class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, game, x, y, x_pos=0, y_pos=0, width=Config.TILE_SIZE, height=Config.TILE_SIZE, layer=0, groups=None, spritesheet=None):
        self._layer = layer
        groups = (game.all_sprites, ) if groups == None else (game.all_sprites, groups)
        super().__init__(groups)
        self.game = game
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        

        if spritesheet == None:
            self.image = pygame.Surface([self.width, self.height])
            self.image.fill(Config.GREY)
        else:
            self.spritesheet = spritesheet
            self.image = self.spritesheet.get_sprite(
                self.x_pos,
                self.y_pos,
                self.width,
                self.height
            )
        self.rect = self.image.get_rect()
        self.rect.x = x * Config.TILE_SIZE
        self.rect.y = y * Config.TILE_SIZE

    def scale(self, factor=2):
        self.rect.width *= factor
        self.rect.height *= factor
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


class PlayerSprite(BaseSprite):
    def __init__(self, game, x, y, **kwargs):
        super().__init__(game, x, y, groups=game.players, layer=2, **kwargs)
        self.speed = 3
        self.color = Config.RED
        self.anim_counter = 0
        self.animation_frames = [0]
        self.current_frame = 0
        self.animation_duration = 30
        self.image = pygame.image.load("res/Fertig hinten.png")
        self.has_knife = False
        

   

    def animate(self, x_diff):
        self.anim_counter += abs(x_diff)
        new_frame = round(self.anim_counter / self.animation_duration) % len(self.animation_frames)
        if self.current_frame != new_frame:
            new_pos = self.animation_frames[new_frame]
            self.image = self.spritesheet.get_sprite(new_pos, self.y_pos, self.width, self.height)
            self.current_frame = new_frame
            self.anim_counter = self.anim_counter % (len(self.animation_frames) * self.animation_duration)

    
    def update(self):
        self.handle_movement()
        self.check_collision()


    def handle_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x = self.rect.x - self.speed
            self.image = pygame.image.load("res/Fertig links.png")
        if keys[pygame.K_RIGHT]:
            self.rect.x = self.rect.x + self.speed
            self.image = pygame.image.load("res/Fertig rechts.png")
        if keys[pygame.K_UP]:
            self.rect.y = self.rect.y - self.speed
            self.image = pygame.image.load("res/Fertig hinten.png")
        if keys[pygame.K_DOWN]:
            self.rect.y = self.rect.y + self.speed
            self.image = pygame.image.load("res/Fertig vorn.png")
        self.update_camera()



    def update_camera(self):
        x_c, y_c = self.game.screen.get_rect().center
        x_diff = x_c - self.rect.centerx
        y_diff = y_c - self.rect.centery
        for sprite in self.game.all_sprites:
            if sprite in self.game.interface:
                continue
            sprite.rect.x += x_diff
            sprite.rect.y += y_diff
        self.animate(x_diff)

        # Shift Background
        self.game.bg_x += x_diff * Config.BG_SPEED
        if self.game.bg_x > Config.WINDOW_WIDTH:
            self.game.bg_x = -Config.WINDOW_WIDTH
        elif self.game.bg_x < -Config.WINDOW_WIDTH:
            self.game.bg_x = Config.WINDOW_WIDTH


    def is_standing(self, hit):
        if abs(hit.rect.top - self.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True

    def hit_head(self, hit):
        if abs(self.rect.top - hit.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True


    def check_collision(self):
        
        
        hits = pygame.sprite.spritecollide(self, self.game.ground, False)
        for hit in hits:
            if self.is_standing(hit):
                self.rect.bottom = hit.rect.top
                break
            if self.hit_head(hit):
                self.rect.top = hit.rect.bottom
                break

        hits = pygame.sprite.spritecollide(self, self.game.ground, False)
        for hit in hits:
            hit_dir = hit.rect.x - self.rect.x
            if hit_dir < 0:
                self.rect.left = hit.rect.right
            else:
                self.rect.right = hit.rect.left

        hits = pygame.sprite.spritecollide(self, self.game.Tür, False)
        for hit in hits:
            if self.is_standing(hit):
                self.rect.bottom = hit.rect.top
                break
            if self.hit_head(hit):
                self.rect.top = hit.rect.bottom
                break

        hits = pygame.sprite.spritecollide(self, self.game.Tür, False)
        for hit in hits:
            hit_dir = hit.rect.x - self.rect.x
            if hit_dir < 0:
                self.rect.left = hit.rect.right
            else:
                self.rect.right = hit.rect.left




        hits = pygame.sprite.spritecollide(self, self.game.knife, False)
        if hits:
            for hit in hits:
                knife(self.game, 0, 0)
                hit.kill()
                self.has_knife = True
                

        hits = pygame.sprite.spritecollide(self, self.game.items, False)
        if hits and self.has_knife:
            for hit in hits:
                BildKaputt(self.game, hit.rect.x, hit.rect.y)
                hit.kill()
                
                
                
                

        hits = pygame.sprite.spritecollide(self, self.game.Tür, False)
        if hits:
            for hit in hits:
                pass

class ToolbarSlot(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/knife.png")
        }
        super().__init__(game, x, y, groups=game.knife, layer=1, **img_data)

class ToolbarBackground(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Toolbar.png"),
            'x_pos':0,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.interface, layer=4, **img_data)

class knife(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/knife.png"),
            'x_pos':0,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.interface, layer=4, **img_data)

class WallLeft(BaseSprite):
    def __init__(self, game, x, y, width=Config.TILE_SIZE, height=Config.TILE_SIZE):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 0,
            'y_pos': 32
        }
        self.width = width
        self.height = height
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)

class WallTop(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 32,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)

class WallEckenLeftTop(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 0,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)

class WallRight(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 64,
            'y_pos': 32
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)

class WallEckenRightTop(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 64,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)

class WallEckenRightBottom(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 64,
            'y_pos': 64
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data) 

class WallEckenLeftBottom(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 0,
            'y_pos': 64
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)  

class WallBottom(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mauern.png"),
            'x_pos': 32,
            'y_pos': 64
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)      

class Laterne(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Laterne.png"),
            'x_pos': 0,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)  


class Floor(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Boden_.png"),
            'x_pos': 0,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.floor, layer=1, **img_data)

class Schrank:
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet('res/player.png')
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)

class Bild(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Gemälde (ganz).png")
        }
        super().__init__(game, x, y, groups=game.items, layer=1, **img_data) 

class BildKaputt(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Gemälde (kaputt).png")
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data) 

class Tür(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Tür.png")
        }
        super().__init__(game, x, y, groups=game.Tür, layer=1, **img_data) 

class Schrank(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Schrank.png"),
            'x_pos': 0,
            'y_pos': 0
        }
        super().__init__(game, x, y, groups=game.ground, layer=1, **img_data)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)
        self.screen = pygame.display.set_mode( (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT) ) 
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("res/bg-small.png")
        self.bg_x = 0
        pygame.display.set_caption("Unser erstes Pygame-Spiel")

     




    
    def load_map(self, mapfile):
        with open(mapfile, "r") as f:
            for (y, lines) in enumerate(f.readlines()):
                for (x, c) in enumerate(lines):
                    Floor(self, x, y)
                    if c == "l":   
                        WallLeft(self, x, y)
                    if c == "p":
                        self.player = PlayerSprite(self, x, y)
                    if c == "t":
                        WallTop(self, x, y)
                    if c == "e":
                        WallEckenLeftTop(self, x, y)
                    if c == "r":
                        WallRight(self, x, y)
                    if c == "E": 
                        WallEckenLeftTop(self, x, y)
                    if c == "R":
                        WallEckenRightTop(self, x, y)
                    if c == "T":
                        WallEckenLeftBottom(self, x, y)
                    if c == "Z":
                        WallEckenRightBottom(self, x, y)
                    if c == "b":
                        WallBottom(self, x, y)
                    if c == "S":
                        Schrank(self, x, y)
                    if c == "B":
                        
                        Bild(self, x, y)
                    if c == "K":
                        ToolbarSlot(self, x, y)
                    if c == "L":
                        Laterne(self, x, y)
                    if c == "D":
                        Tür(self, x, y)
                    if c == "s":
                        Schrank(self, x, y)





    def new(self):
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground = pygame.sprite.LayeredUpdates()
        self.floor = pygame.sprite.LayeredUpdates()
        self.players = pygame.sprite.LayeredUpdates()
        self.interface = pygame.sprite.LayeredUpdates()
        self.items = pygame.sprite.LayeredUpdates()
        self.knife = pygame.sprite.LayeredUpdates()
        self.Tür = pygame.sprite.LayeredUpdates()
        self.Toolbarbackground = ToolbarBackground(self, 0, 0)  


        self.load_map("maps/level-01.txt")
        

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False

    

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.blit(self.bg, (self.bg_x, 0))
        tmp_bg = pygame.transform.flip(self.bg, True, False)
        second_x = Config.WINDOW_WIDTH + self.bg_x
        if self.bg_x > 0:
            second_x -= 2*Config.WINDOW_WIDTH
        self.screen.blit(tmp_bg, (second_x, 0))

        self.all_sprites.draw(self.screen)
        pygame.display.update()

    def game_loop(self):
        counter = 1000
        while self.playing:
            self.handle_events()
            self.update()
            self.draw()
            counter_text = self.font.render(f'{counter}', False, (Config.WHITE))
            self.screen.blit(counter_text, (620, 0))
            counter -= 1
            pygame.display.flip()
            self.clock.tick(Config.FPS)
            if counter == 0:
                break

    def GameOver(self):
        while True:
            self.screen.fill(Config.WHITE)
            display_text = pygame.image.load("res/GameOver.png")
            display_text = pygame.transform.scale(display_text,(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
            self.screen.blit(display_text, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(Config.FPS)
            

            pygame.event.get()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                break
            
                    
    
def main():
    g = Game()
    
    
    g.new()

    g.game_loop()

    g.GameOver()

    pygame.quit()
    sys.exit()
