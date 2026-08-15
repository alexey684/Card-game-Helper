from PIL import Image, ImageChops, ImageOps, ImageGrab
from utils import resource_path
import numpy as np
import keyboard

red = [0, 0, 10868, 8161]
black = [61000, 50500, 549, 533]
GLOBAL_NUM = 0

y_min1, y_max1, y_min2, y_max2 = 356, 390, 395, 429
top = [450, 535, 619, 705, 792, 879]
bot = [443, 529, 615, 703, 795, 883]
add = [15, 15, 15, 15, 15, 15]

rank_name = ["Шестерка", "Семерка", "Восьмерка", "Девятка", "Десятка", "Валет", "Дама", "Король", "Туз"]
suit_name = ["пик", "треф", "бубей", "червей"]

def make_screen(cnt):
    screenshot = ImageGrab.grab()
    cut_screen(screenshot, cnt)

def cut_screen(scr, card_number=0):
    card = []
    for i in range(6):
        card.append(scr.crop((top[i], y_min1, top[i]+add[i], y_max1)))
        card.append(scr.crop((bot[i], y_min2, bot[i]+add[i], y_max2)))

    for i in range(10, len(card)):
        # card[i].save(f'{i}.png')
        res = split_card(card[i], i, card_number)
        if i % 2 == 0 and res == "None":
            break

def load_suits():
    sp = Image.open(resource_path('suits/spade.png'))
    cl = Image.open(resource_path('suits/club.png'))
    dia = Image.open(resource_path('suits/diamond.png'))
    hea = Image.open(resource_path('suits/heart.png'))

    return [sp, cl, dia, hea]

def split_card(card, index, card_number=1000):
    rank = card.crop((0, 0, 15, 17))
    suit = card.crop((0, 17, 15, 34))

    rank = ImageOps.grayscale(rank)

    s = detect_suit(suit)
    if s == "None":
        print("Карты нет")
        return "None"

    # r = detect_rank(rank, index)

    rank.save(f'data/{index}/{card_number}.png')
    # suit.save('su.png')

    # print(r)  # + " " + s)
    return rank


def detect_suit(suit):
    np_image = np.array(suit)

    # rd = [calc_r_g_channels(s)[0] for s in arrays]
    red_our, black_our = calc_r_g_channels(np_image)

    if red_our > 5000:
        if abs(red_our - red[2]) < abs(red_our - red[3]):
            return suit_name[2]
        else:
            return suit_name[3]
    elif black_our > 10000:
        if black_our > 80000:
            return "None"
        if abs(black_our - black[0]) < abs(black_our - black[1]):
            return suit_name[0]
        else:
            return suit_name[1]
    else:
        return "None"

def detect_rank(rank, index):
    c = cut_right(calc_struct(rank, index))

    diff = [calc_intersec(c, rk) for rk in etalon_ranks]
    return rank_name[np.argmax(diff)]
    # for rk in etalon_ranks:
    #     print(calc_intersec(c, rk))

def count_etalons():
    all_ranks = [Image.open(resource_path(f'ranks/{i}.png')) for i in range(9)]
    res = [cut_right(calc_struct(card)) for card in all_ranks]

    return res

def calc_intersec(c1, c2):
    res = 0
    for i in range(17):
        for j in range(15):
            a, b = c1[i][j], c2[i][j]
            if a == b:
                if a == b == 128:
                    res += 0.3
                if a == b == 0:
                    res += 1
                if a == b == -1:
                    res += 0.3

    return res


def calc_struct(card, index=100):
    im = np.array(card)

    skip = 0
    if index < 4:
        skip = 3
    if index == 4:
        skip = 2

    black, i_start, j_start = 0, 0, 0
    for i in range(17):
        for j in range(skip, 15):
            if im[i][j] == 0:
                black += 1

        if black > 0:
            i_start = i
            break

    black = 0
    for j in range(skip, 15):
        for i in range(17):
            if im[i][j] == 0:
                black += 1

        if black > 0:
            j_start = j
            break

    res = []
    for i in range(i_start, 17+i_start):
        row = []
        for j in range(j_start, 15+j_start):
            if i < 17 and j < 15:
                row.append(0 if im[i][j] == 0 else 128)
            else:
                row.append(128)

        res.append(row)

    return res


def cut_right(arr):
    black, j_end, i_end = 0, 0, 0
    for j in reversed(range(15)):
        for i in range(17):
            if arr[i][j] == 0:
                black += 1

        if black > 0:
            j_end = j+1
            break

    black = 0
    for i in reversed(range(17)):
        for j in range(15):
            if arr[i][j] == 0:
                black += 1

        if black > 0:
            i_end = i + 1
            break

    for i in range(i_end, 17):
        for j in range(15):
            arr[i][j] = -1

    for i in range(17):
        for j in range(j_end, 15):
            arr[i][j] = -1

    return arr


def calc_r_g_channels(img):
    red1, grey = 0, 0
    for i in range(17):
        for j in range(15):
            r,g,b = int(img[i][j][0]), int(img[i][j][1]), int(img[i][j][2])
            if max(r,g,b) - min(r,g,b) > 100:
                red1 += r
            if max(r,g,b) < 128:
                grey += 255*3 - (r+g+b)

    return red1, grey


def on_press_z(event):
     if event.name == 'z':
         pass

     print('z нажата')

# suits = load_suits()
# arrays = [np.array(s) for s in suits] capitancrew7972
# etalon_ranks = count_etalons()
#
# im = '22.png'
# cut_screen(Image.open(im))

cnt = 1000
while True:
    keyboard.wait('z')
    make_screen(cnt)
    cnt += 1
