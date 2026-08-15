import ctypes
import sys
import pygame
from PIL import Image, ImageChops, ImageOps, ImageGrab
import numpy as np
import keyboard
from win32gui import SetWindowPos
import win32con
from utils import resource_path

class Game:
    red = [0, 0, 10868, 8161]
    black = [61000, 50500, 549, 533]

    y_min1, y_max1, y_min2, y_max2 = 356, 390, 395, 429
    top = [450, 535, 619, 705, 792, 879]
    bot = [443, 529, 615, 703, 795, 883]
    add = [15, 15, 15, 15, 15, 15]

    butt_dict = {"right": "right", "left": "left", "up": "opposite", "down": "bito"}


    def __init__(self):
        self.saved_ranks = self.load_images()
        self.card_status = ["ingame"]*36

        ctypes.windll.user32.SetProcessDPIAware()

        pygame.init()

        self.screen = pygame.display.set_mode((247, 665))
        self.bito_im = pygame.image.load(resource_path('assets/bito.png'))
        self.grey, self.blue, self.green = Game.get_rects()


        SetWindowPos(pygame.display.get_wm_info()['window'], win32con.HWND_TOPMOST, 0, 0, 0, 0,
                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        self.board = pygame.image.load(resource_path('assets/board3.png'))
        self.screen.blit(self.board, (0,0))
        pygame.display.flip()

    @staticmethod
    def get_rects():
        left_op = pygame.image.load(resource_path('assets/tuning1.bmp'))
        opposite_op = pygame.image.load(resource_path('assets/tuning2.bmp'))
        right_op = pygame.image.load(resource_path('assets/tuning3.bmp'))

        return left_op, opposite_op, right_op


    def reset(self):
        for i in range(36):
            self.card_status[i] = "ingame"

        self.screen.blit(self.board, (0, 0))
        pygame.display.flip()

    def redraw(self):
        self.screen.blit(self.board, (0, 0))
        for rk in range(9):
            for s in range(4):
                x = 4 + 61*s
                y = 66 + 58*rk

                if rk == 8: y += 1
                if self.card_status[(8-rk)*4+s] == "bito":
                    self.screen.blit(self.bito_im, (x,y))
                if self.card_status[(8-rk)*4+s] == "left":
                    self.screen.blit(self.grey, (x,y))
                if self.card_status[(8-rk)*4+s] == "opposite":
                    self.screen.blit(self.blue, (x,y))
                if self.card_status[(8-rk)*4+s] == "right":
                    self.screen.blit(self.green, (x,y))


    def main(self):
        keyboard.on_press_key("a", lambda _: self.handle_button_press("left"))
        keyboard.on_press_key("d", lambda _: self.handle_button_press("right"))
        keyboard.on_press_key("w", lambda _: self.handle_button_press("up"))
        keyboard.on_press_key("s", lambda _: self.handle_button_press("down"))
        keyboard.on_press_key("r", lambda _: self.reset())
        keyboard.on_press_key(" ", lambda _: self.handle_button_press("down"))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


    def handle_button_press(self, button):
        scr = Game.make_screen()
        active_cards = self.screen_analyze(scr)

        status = Game.butt_dict[button]
        for num in active_cards:
            self.card_status[num] = status

        if len(active_cards) > 0:
            self.redraw()
            pygame.display.flip()

    def load_images(self):
        data = []
        for pos in range(12):
            i_pos = []
            for rank in range(9):
                i_pos.append(Image.open(resource_path(f'ranks/{pos}/{rank}.png')))

            data.append(np.array(i_pos, dtype=np.int32))

        return data

    @staticmethod
    def make_screen():
        return ImageGrab.grab()

    def screen_analyze(self, scr):
        cards = []
        for i in range(6):
            cards.append(scr.crop((Game.top[i], Game.y_min1, Game.top[i] + Game.add[i], Game.y_max1)))
            cards.append(scr.crop((Game.bot[i], Game.y_min2, Game.bot[i] + Game.add[i], Game.y_max2)))

        active_cards = []
        for card_pos in range(12):
           suit, rank = self.analyze_card(cards[card_pos], card_pos)

           if suit == "break":
                break
           if suit == -1:
                continue

           card_num = rank*4 + suit
           active_cards.append(card_num)

        return active_cards


    def analyze_card(self, card, card_pos):
        suit_im, rk_im = self.split_card(card)

        suit = self.detect_suit(suit_im)
        if suit == -1:
            if card_pos % 2 == 0:
                return "break", -1

            return -1, -1

        rank = self.detect_rank(rk_im, card_pos)

        return suit, rank


    @staticmethod
    def split_card(card):
        rank = card.crop((0, 0, 15, 17))
        suit = card.crop((0, 17, 15, 34))

        rank = ImageOps.grayscale(rank)

        return suit, rank

    @staticmethod
    def detect_suit(suit_image):
        np_image = np.array(suit_image)

        red_our, black_our = Game.calc_r_g_channels(np_image)
        if black_our > 80000:
            return -1

        if red_our > 5000:
            if abs(red_our - Game.red[2]) < abs(red_our - Game.red[3]):
                return 0
            else:
                return 2
        elif black_our > 10000:
            if abs(black_our - Game.black[0]) < abs(black_our - Game.black[1]):
                return 1
            else:
                return 3
        else:
            return -1

    @staticmethod
    def calc_r_g_channels(img):
        red, grey = 0, 0
        for i in range(17):
            for j in range(15):
                r, g, b = int(img[i][j][0]), int(img[i][j][1]), int(img[i][j][2])
                if max(r, g, b) - min(r, g, b) > 100:
                    red += r
                if max(r, g, b) < 128:
                    grey += 255 * 3 - (r + g + b)

        return red, grey

    def detect_rank(self, rk_im, card_pos):
        our_rank = np.array(rk_im, dtype=np.int32)
        diff = [Game.cmp(our_rank, rk) for rk in self.saved_ranks[card_pos]]

        return np.argmin(diff)

    @staticmethod
    def cmp(im1, im2):
        res = 0
        for i in range(17):
            for j in range(15):
                    res += abs(im1[i][j] - im2[i][j])


        return res


