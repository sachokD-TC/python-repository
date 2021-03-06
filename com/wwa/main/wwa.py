import copy

import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from sound_play import Sound_play as sound

from com.wwa.main.levels import levels
from com.wwa.players.cowboy import Cowboy
from com.wwa.players.sun import Sun

TMW_DESERT_SPACING_PNG = '../map/tmw_desert_spacing.png'

PIC_ = '../pic/'

PIC_GAME_OVER_PNG = '%sgame_over.png' % PIC_

LEVEL_COMPLETED_PNG = '%slevel_completed.png' % PIC_

LEVEL_PNG = '%slevel.png' % PIC_

CLOCK_PNG = '%sclock.png' % PIC_

SCORES_BROWN_PNG = '%sscores_brown.png' % PIC_

TIME_TAKEN_Y = 400

LAYER_DONE_PERCENT = 500

CACTUS_FINAL_Y = 300

FINAL_SCORES_X = 190 + 100

FONT_NAME = 'JOKERMAN'

BOXES = "boxes"

PIC_OBJS = 'pic_objs'

EXIT = 'exit'

TELEPORT_LEVEL = 'teleport'

WIN_WIDTH = 800
WIN_HEIGHT = 800

SCORE_POS_X = 520
SCORE_POS_Y = 750

LEVEL_POS_X = 250
LEVEL_POS_Y = 400

SCORE_COUNT_POS_X = SCORE_POS_X + 220
SCORE_AND_CACTUS_POS_Y = SCORE_POS_Y + 5
CACTUS_COUNT_POS_X = SCORE_POS_X + 80

TIME_POS_X = 650
TIME_POS_Y = 15

TIME_INDEX = 1
LEVEL_INDEX = 0

red = pygame.Color(153, 0, 0)


class Wwa():
    def __init__(self, level, sound_on, godmode):
        pygame.init()
        self.time = levels[level - 1][TIME_INDEX]
        self.rect = []
        self.suns = []
        self.level = level
        self.pic_obj_level = None
        self.clock = pygame.time.Clock()
        self.cactus_count = 0
        self.life = 100
        self.godmode = godmode
        if godmode:
            self.life = 10000
        self.game_display = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.teleports = None
        self.pytmx_map = load_pygame("../map//" + levels[level - 1][LEVEL_INDEX] + ".tmx")
        self.score_image = pygame.image.load(SCORES_BROWN_PNG)
        self.clock_image = pygame.image.load(CLOCK_PNG)
        self.level_image = pygame.image.load(LEVEL_PNG)
        self.finish_background = pygame.image.load(LEVEL_COMPLETED_PNG)
        self.game_over_pic = pygame.image.load(PIC_GAME_OVER_PNG)
        self.sound = sound(sound_on)
        self.sound_on = sound_on
        self.main_loop()

    def put_text(self, t, font_name, font_size, x, y, color):
        font = pygame.font.SysFont(font_name, font_size)
        text = font.render(str(t), True, color)
        self.game_display.blit(text, (x, y))

    def redraw_pics(self):
        for layer in self.pytmx_map.visible_layers:
            if layer.name == PIC_OBJS:
                self.pic_obj_level = layer
            if isinstance(layer, pytmx.TiledTileLayer):
                for x in range(0, 40):
                    for y in range(0, 40):
                        image = self.pytmx_map.get_tile_image(x, y, 0)
                        if image != None and (x, y) not in self.rect:
                            self.pics.blit(image, (32 * x, 32 * y))
                        else:
                            surface_image = pygame.image.load(TMW_DESERT_SPACING_PNG)
                            self.pics.blit(surface_image, (32 * x, 32 * y), (5 * 32 + 6, 3 * 32 + 4, 32, 32))

    def show_level(self):
        self.game_display.fill(pygame.Color(244, 215, 65))
        pygame.display.update()
        self.game_display.blit(self.level_image, (LEVEL_POS_X, LEVEL_POS_Y))
        self.put_text('Level ' + str(self.level), 'JOKERMAN', 25, LEVEL_POS_X + 100, LEVEL_POS_Y + 5, (255, 255, 255))
        pygame.display.update()
        pygame.time.delay(3000)

    def show_final_scores(self):
        self.put_text('Cactuses ' + str(self.cactus_count), 'JOKERMAN', 25, FINAL_SCORES_X, CACTUS_FINAL_Y, (0, 0, 0))
        time_taken = levels[self.level - 1][TIME_INDEX] - self.time
        self.put_text('Time ' + str(time_taken), 'JOKERMAN', 25, FINAL_SCORES_X, TIME_TAKEN_Y, (0, 0, 0))
        percent_done = (float)(self.cactus_count) / int(len(self.pic_obj_level)) * 100
        self.put_text('Layer done on ' + str(format(percent_done, '.2f')) + "%", 'JOKERMAN', 25, FINAL_SCORES_X,
                      LAYER_DONE_PERCENT, (0, 0, 0))
        pygame.display.update()
        pygame.time.delay(50)

    def show_finish(self):
        self.game_display.blit(self.finish_background, (190, 100))
        pygame.display.update()
        self.show_final_scores()
        pygame.time.delay(3000)
        self.level += 1
        if self.level > len(levels):
            self.loop = False
        else:
            Wwa(self.level, self.sound_on, self.godmode)
            self.loop = False

    def minus_life(self):
        self.life -= 1
        self.put_text(self.life, FONT_NAME, 25, SCORE_COUNT_POS_X, SCORE_AND_CACTUS_POS_Y,
                      (255, 255, 255))
        self.sound.play_hit_sound()
        if self.life <= 0:
            self.show_game_over()
            self.loop = False

    def show_game_over(self):
        self.game_display.blit(self.game_over_pic, (190, 100))
        pygame.display.update()
        self.sound.play_game_over_sound()
        pygame.time.delay(3000)

    def update_sun(self):
        for s in self.suns:
            if not self.cowboy.is_step_back:
                s.update(-self.cowboy.movement_dict[self.cowboy.movement][0],
                         -self.cowboy.movement_dict[self.cowboy.movement][1])
            else:
                s.update(0, 0)
            s.draw(self.game_display)

    def check_sun_collide(self):
        for s in self.suns:
            if self.cowboy.rect.colliderect(s.rect):
                self.minus_life()

    def main_loop(self):
        for s in levels[self.level-1][2]:
            self.suns.append(Sun(copy.copy(s)))
        self.cowboy = Cowboy()
        self.background = pygame.Surface((42 * 32, 42 * 32))
        self.pics = pygame.Surface((42 * 32, 42 * 32))
        self.loop = True
        self.event = None
        self.redraw_pics()
        self.show_level()

        while (self.loop):
            self.time -= 1;
            self.cowboy.is_step_back = False
            for event in pygame.event.get():
                pass
            layer_index = 0
            for layer in self.pytmx_map.visible_layers:
                layer_index += 1
                if isinstance(layer, pytmx.TiledObjectGroup):
                    if layer.name == EXIT:
                        for obj in layer:
                            if pygame.Rect(obj.x + self.cowboy.pos_x, obj.y + self.cowboy.pos_y, obj.width,
                                           obj.height).colliderect(self.cowboy.rect) == True:
                                self.show_finish()
                    if layer.name == PIC_OBJS:
                        for obj in layer:
                            if pygame.Rect(obj.x + self.cowboy.pos_x, obj.y + self.cowboy.pos_y, obj.width,
                                           obj.height).colliderect(self.cowboy.rect) == True:
                                cactus = (round(obj.x / 32), round(obj.y / 32))
                                if cactus not in self.rect:
                                    self.cactus_count += 1
                                    self.put_text(self.cactus_count, FONT_NAME, 25, CACTUS_COUNT_POS_X,
                                                  SCORE_AND_CACTUS_POS_Y, (255, 255, 255))
                                    self.rect.append(cactus)
                                    self.redraw_pics()
                                    self.sound.play_pick_sound()
                                    break
                    if layer.name == BOXES:
                        for obj in layer:
                            if pygame.Rect(obj.x + self.cowboy.pos_x, obj.y + self.cowboy.pos_y, obj.width,
                                           obj.height).colliderect(self.cowboy.rect) == True:
                                self.cowboy.step_back()
                                self.cowboy.is_step_back = True
                                self.minus_life()
                                break
            self.check_sun_collide()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.sound_on = not self.sound_on
                    self.sound = sound(self.sound_on)
                elif event.key == pygame.K_F4:
                    self.godmode = not self.godmode
                    if self.godmode:
                        self.life = 10000
                    else:
                        self.life = 100

            self.cowboy.update(event)
            self.game_display.blit(self.pics, (self.cowboy.pos_x, self.cowboy.pos_y))
            self.game_display.blit(self.score_image, (SCORE_POS_X - 20, SCORE_POS_Y - 10))
            self.update_sun()
            self.game_display.blit(self.clock_image, (TIME_POS_X - 100, TIME_POS_Y - 17))
            self.put_text(self.life, FONT_NAME, 25, SCORE_COUNT_POS_X, SCORE_AND_CACTUS_POS_Y, (255, 255, 255))
            self.put_text(self.cactus_count, FONT_NAME, 25, CACTUS_COUNT_POS_X, SCORE_AND_CACTUS_POS_Y,
                          (255, 255, 255))
            self.put_text(self.time, FONT_NAME, 25, TIME_POS_X, TIME_POS_Y,
                          (255, 255, 255))
            self.cowboy.draw(self.game_display)
            self.clock.tick(60)
            pygame.display.update()
