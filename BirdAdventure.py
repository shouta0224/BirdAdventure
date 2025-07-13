import pygame
import sys
import random
import math
from tkinter import messagebox
import numpy as np
import logging

screen = pygame.display.set_mode((1280, 960))  # スクリーン初期化 解像度設定

WHITE = (255, 255, 255)

img_bg = pygame.image.load("img\\bg_space.png")  # 背景画像
img_tb = pygame.image.load("img\\textbox.png") # テキストボックス
img_chara = [pygame.image.load("img\ch_bird_1.png"),  # 主人公の画像
             pygame.image.load("img\ch_bird_2.png"),
             pygame.image.load("img\ch_bird_died.png")
             ]
img_tama = pygame.image.load("img\\tama.png")  # 弾の画像
img_tama_2 = pygame.image.load("img\\tama_2.png")  # 弾の画像
img_boss = [pygame.image.load("img\\boss_1.png")]
img_speaker = [pygame.image.load("img\\sp_kari.png")] # テキストボックスのキャラ

tmr = 0  # 時間管理変数
idx = 0 # 0
ch_x = 565  # 主人公のX座標 初期化
ch_y = 810  # 同じくY座標
ch_hp_max = 10
ch_hp = ch_hp_max # 残機
CH_SPD = 10  # 主人公の速さ
TA_MAX = 300  # 弾の量
ta_x = [-100] * TA_MAX  # 弾のX座標 初期化
ta_y = [-100] * TA_MAX  # 同じくY座標
ta_kazu = TA_MAX  # 弾の数
TA_SPD = 10  # 弾の速さ
ta_kakuritsu = 1
ta_kakudo = [270] * TA_MAX
ta_num = 0
TA_2_KAZU = 200  # 一度に画面に描画される最大量
ta_2_x = [-100] * TA_2_KAZU  # 弾のX座標 初期化 #弾2は主人公が出す弾
ta_2_y = [-100] * TA_2_KAZU  # 同じくY座標
ta_utsu = 0
gmov = 0  # ゲームオーバーの原因の玉
msbx = 0  # メッセージボックス
ATARIHANTEI_X = 25  # 35
ATARIHANTEI_Y = 30  # 40
bs_x = 0
bs_y = 0
BS_UGOKUHINDO = 2  # 2
bs_hp = 0
bs_hp_max = 0
bs_fight = 0
level = 0
ii = 0
MAX_LEVEL = 1
FONT_PATH = "fnt/ipaexg.ttf"
sinario_num = 0
is_press_enter = 0 #文字送りのキーを押しているか
is_pull_enter = 1
#ZandEnter = 0

ta_utsu_Z = 0
ta_utsu_enter = 0

TXT_CHA = [ # テキストボックスシステムのキャラをまとめたリスト
    ["鳥", 0] # 左がキャラの名前。右がキャラの画像の番号。img_speakerに対応している。
]

SINARIO = [ # シナリオ。テキストファイルで管理できたらうれしい 
    ["やあ。僕は鳥だよ。", 0], # 左が喋る内容。右がキャラクターID。TXT_CHAに対応。
    ["鳥は種類だろだって?", 0],
    ["違う。", 0],
    ["種類が鳥なんじゃなくて名前が鳥。", 0],
    ["ここ入れないとなんかバグる。長さにも入れる。(boss.sn)", 0]
]

def control():  # 主人公の操作
    global ch_x, ch_y, ta_utsu, ta_utsu_Z, ta_utsu_enter
    key = pygame.key.get_pressed()
    if key[pygame.K_UP]:
        ch_y = ch_y - CH_SPD
        if ch_y < 0:
            while ch_y < 0:
                ch_y = ch_y + 1
    if key[pygame.K_DOWN]:
        ch_y = ch_y + CH_SPD
        if ch_y > 810:
            while ch_y > 810:
                ch_y = ch_y - 1
    if key[pygame.K_RIGHT]:
        ch_x = ch_x + CH_SPD
        if ch_x > 1130:
            while ch_x > 1130:
                ch_x = ch_x - 1
    if key[pygame.K_LEFT]:
        ch_x = ch_x - CH_SPD
        if ch_x < 0:
            while ch_x < 0:
                ch_x = ch_x + 1
    ta_utsu_Z = (ta_utsu + 1) * key[pygame.K_z] # 弾を打つ
    ta_utsu_enter = (ta_utsu + 1) * key[pygame.K_RETURN]
    if not ta_utsu_Z == 0:
        ta_utsu = ta_utsu_Z
    elif not ta_utsu_enter == 0:
        ta_utsu = ta_utsu_enter
    else:
        ta_utsu = 0
    if ta_utsu % 5 == 1:
        ta_utsu = 1


def event():
    global idx, ta_utsu, is_press_enter, is_pull_enter
#    ZandEnter = 0
    is_press_enter = 0
    is_pull_enter = 1
    pygame.event.pump()  # よくわからん。おまじないらしい。
    key = pygame.key.get_pressed()  # キーが押されているかを取得
    for event in pygame.event.get():  # WIndowのバツボタンが押されたとき
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Rでリセット
                idx = 0
            if event.key == pygame.K_z or event.key == pygame.K_RETURN: # Zかエンターで文字送り
                is_press_enter = 1
#            else:
#                is_press_enter = 0
#                is_pull_enter = 1

"""
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_z or event.key == pygame.K_RETURN: # Zかで文字送り
                ZandEnter = ZandEnter + 1
            if ZandEnter == 2:
                is_press_enter = 0
                is_pull_enter = 1
                print("C")

"""

def tama(): # 敵の弾
    global ta_kakuritsu, gmov, idx, screen, ch_hp, ch_hp_max
    t = 0
    for i in range(ta_kazu):
        if ta_y[i] != -100:  # 有効なら
            ta_x[i] = ta_x[i] + TA_SPD * math.cos(math.radians(ta_kakudo[i]))
            ta_y[i] = ta_y[i] + TA_SPD * math.sin(math.radians(ta_kakudo[i]))  # 弾を動かす
            if ta_y[i] > 960:  # 画面外なら
                ta_y[i] = -100  # 無効化
            else:
                dx = abs((ch_x + 75) - (ta_x[i] + 15))
                dy = abs((ch_y + 75) - (ta_y[i] + 60))
                if dx <= ATARIHANTEI_X and dy <= ATARIHANTEI_Y:
                    pygame.mixer.init()
                    se_damage_2 = pygame.mixer.Sound("se\damage_2.ogg")
                    se_damage_2.play()
                    ch_hp = ch_hp - 1
                    print(ch_hp)
                    if ch_hp <= 0:
                        gmov = i
                        idx = 2
                    else:
                        ta_y[i] = -100  # 無効化
                img_danmaku = pygame.transform.rotozoom(img_tama, 90 - ta_kakudo[i], 1.0)
                screen.blit(img_danmaku, [ta_x[i], ta_y[i]])  # 描画
        else:
            if i < 101:
                if t == 0:
                    r = random.randint(1, 1000)
                    if r <= ta_kakuritsu:  # 確率で弾が出現
                        t = 1
                        ta_y[i] = -90
                        r = random.randint(0, 1250)  # 弾のX座標
                        ta_x[i] = r
                        ta_kakudo[i] = 90
                        img_danmaku = pygame.transform.rotozoom(img_tama, 90 - ta_kakudo[i], 1.0)
                        screen.blit(img_danmaku, [ta_x[i], ta_y[i]])  # 描画
                elif t == 1:
                    r = random.randint(1, 5000)
                    if r <= ta_kakuritsu:  # 確率で弾が出現
                        t = 2
                        ta_y[i] = -90
                        r = random.randint(0, 1250)  # 弾のX座標
                        ta_x[i] = r
                        ta_kakudo[i] = 90
                        img_danmaku = pygame.transform.rotozoom(img_tama, 90 - ta_kakudo[i], 1.0)
                        screen.blit(img_danmaku, [ta_x[i], ta_y[i]])  # 描画
                    else:
                        t = 0
                elif t == 2:
                    t = 0


def tama_2(): # 主人公の弾
    global ta_2_x, ta_2_y, TA_2_KAZU, ta_utsu, bs_hp
    global idx, screen, level
    t = 0
    for i in range(TA_2_KAZU):
        if ta_2_y[i] != -100:  # 有効なら
            ta_2_y[i] = ta_2_y[i] - TA_SPD  # 弾を動かす
            if ta_2_y[i] < -80:  # 画面外なら
                ta_2_y[i] = -100  # 無効化
            else:
                if bs_fight == 1:
                    dx = abs((bs_x + 150) - (ta_2_x[i] + 15))
                    dy = abs((bs_y + 100) - (ta_2_y[i] + 20))
                    if dx <= 165 and dy <= 70:
                        pygame.mixer.init()
                        se_damage = pygame.mixer.Sound("se\damage.ogg")
                        se_damage.play()
                        bs_hp = bs_hp - 1
                        ta_2_y[i] = -100
                        print(bs_hp)

                screen.blit(img_tama_2, [ta_2_x[i], ta_2_y[i]])  # 描画
        else:
            if t == 0:
                if ta_utsu == 1:  # Zが押されたなら
                    pygame.mixer.init()
                    se_damage = pygame.mixer.Sound("se\hassha.ogg")
                    se_damage.play()
                    t = 1
                    ta_2_y[i] = ch_y
                    ta_2_x[i] = ch_x + 60
                    screen.blit(img_tama_2, [ta_2_x[i], ta_2_y[i]])  # 描画


class Boss:
    def __init__(self, id, hp, size_x, size_y, sinario_ichi, sinario_nagasa):
        self.id = id
        self.hp = hp
        self.sx = size_x
        self.sy = size_y
        self.si = sinario_ichi
        self.sn = sinario_nagasa

    def rdy(self):  # ボスの準備
        global bs_x, bs_y, bs_hp, bs_hp_max
        bs_x = 640 - (self.sx / 2)
        bs_y = -self.sy + ((self.sy / 30) * ii)
        bs_hp = self.hp
        bs_hp_max = self.hp
        screen.blit(img_boss[self.id - 1], [bs_x, bs_y])

    def sinariochu(self):
        global bs_x, bs_y, bs_hp, bs_hp_max
        bs_x = 640 - (self.sx / 2)
        bs_y = -self.sy + (self.sy)
        bs_hp = self.hp
        bs_hp_max = self.hp
        screen.blit(img_boss[self.id - 1], [bs_x, bs_y])

    def gekiha(self):
        pygame.mixer.init()
        se_gekiha = pygame.mixer.Sound("se\\bakuhatsu.ogg")
        se_gekiha.play()

    def attack(self):
        if self.id == 1:
            global ta_num, bs_x, bs_y
            r = random.randint(1, 100)
            if r <= BS_UGOKUHINDO:
                r = random.randint(0, 1280 - self.sx)
                bs_x = r
                r = random.randint(0, self.sy)
                bs_y = r
            r = random.randint(1, 250)
            if r <= ta_kakuritsu:
                for a in range(0, 190, 10):  # 弾幕
                    ta_x[ta_num + 100] = bs_x + 125
                    ta_y[ta_num + 100] = bs_y + 200
                    ta_kakudo[ta_num + 100] = a
                    ta_num = (ta_num + 1) % 200
            screen.blit(img_boss[0], [bs_x, bs_y])


def main():
    global tmr, idx, screen, ii, level
    global ch_x, ch_y, CH_SPD, ch_hp, ch_hp_max
    global TA_MAX, ta_x, ta_y, ka_kazu, TA_SPD, ta_kakuritsu, ta_num
    global ta_2_x, ta_2_y, TA_2_KAZU, ta_utsu
    global gmov, msbx, ATARIHANTEI_X, ATARIHANTEI_Y
    global bs_x, bs_y, bs_fight, bs_hp, bs_hp_max
    global sinario_num, is_press_enter, is_pull_enter
    pygame.init()  # 初期化
    pygame.display.set_caption("シューティング")  # Windowのタイトル
    clock = pygame.time.Clock()  # clockオブジェクト
    font = pygame.font.Font(None, 60)
    while True:
        tmr = tmr + 1  # タイマー進める
        event()
        if idx == 0:  # 戦闘初期化
            gmov = 0
            idx = 1
            ch_x = 565  # 主人公のX座標 初期化
            ch_y = 810  # 同じくY座標
            ta_x = [-100] * TA_MAX  # 弾のX座標 初期化
            ta_y = [-100] * TA_MAX  # 同じくY座標
            msbx = 0
            ta_2_x = [-100] * TA_2_KAZU  # 弾のX座標 初期化 #弾2は主人公が出す弾
            ta_2_y = [-100] * TA_2_KAZU  # 同じくY座標
            ta_kakudo = [270] * TA_MAX
            level = 1
            tmr = 0
            ii = 0
            bs_fight = 0
            ta_kakuritsu = 10
            ch_hp_max = 10
            ch_hp = ch_hp_max
        elif idx == 1:
            ii = ii + 1
            ta_kakuritsu = 10
            bs_fight = 0
            control()
            screen.blit(img_bg, [0, 0])  # 背景描画
            bs_hp = 0

            if tmr % 30 < 15:  # 主人公描画 15フレーム(0.5秒)ごとにアニメーション
                screen.blit(img_chara[0], [ch_x, ch_y])
            else:
                screen.blit(img_chara[1], [ch_x, ch_y])
            tama()
            tama_2()
            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            if ii >= 300:
                idx = 3

        elif idx == 2:  # ゲームオーバー
            screen.blit(img_bg, [0, 0])  # 背景描画
            screen.blit(img_chara[2], [ch_x, ch_y])
            img_danmaku = pygame.transform.rotozoom(img_tama, -90 - ta_kakudo[gmov], 1.0)
            screen.blit(img_danmaku, [ta_x[gmov], ta_y[gmov]])  # 描画
            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            if bs_hp != 0:
                txt_bs_hp = font.render("BOSS HP:{}/{}".format(bs_hp, bs_hp_max), True, WHITE)
                screen.blit(txt_bs_hp, [10, 10])
            if msbx == 0:
                msbx = 1
            elif msbx == 1:
                msbx = 2
                messagebox.showinfo("ゲームオーバー！", "弾に当たってしまいました。OKを押した後Rキーでもう一回プレイできます。")

        elif idx == 3:  # ボス準備
            ta_kakuritsu = 0
            bs_fight = 0
            control()
            screen.blit(img_bg, [0, 0])  # 背景描画

            if tmr % 30 < 15:  # 主人公描画 15フレーム(0.5秒)ごとにアニメーション
                screen.blit(img_chara[0], [ch_x, ch_y])
            else:
                screen.blit(img_chara[1], [ch_x, ch_y])
            tama()
            tama_2()
            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            if level == 1:
                boss = Boss(level, 80, 300, 200, 0, 5)
            ii = 0
            boss.rdy()
            idx = 4

        elif idx == 4:  # ボス出てくる
            ta_kakuritsu = 0
            bs_fight = 0
            control()
            screen.blit(img_bg, [0, 0])  # 背景描画

            if tmr % 30 < 15:  # 主人公描画 15フレーム(0.5秒)ごとにアニメーション
                screen.blit(img_chara[0], [ch_x, ch_y])
            else:
                screen.blit(img_chara[1], [ch_x, ch_y])

            tama()
            tama_2()
            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            txt_bs_hp = font.render("BOSS HP:{}/{}".format(bs_hp, bs_hp_max), True, WHITE)
            screen.blit(txt_bs_hp, [10, -30+(ii*1.3)])

            ii = ii + 1
            boss.rdy()
            if ii == 30:
                ii = 0
                idx = 8

        elif idx == 5:  # ボスの攻撃！
            ta_kakuritsu = 5
            screen.blit(img_bg, [0, 0])  # 背景描画
            bs_fight = 1
            boss.attack()
            control()
            if tmr % 30 < 15:  # 主人公描画 15フレーム(0.5秒)ごとにアニメーション
                screen.blit(img_chara[0], [ch_x, ch_y])
            else:
                screen.blit(img_chara[1], [ch_x, ch_y])

            tama()
            tama_2()
            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            txt_bs_hp = font.render("BOSS HP:{}/{}".format(bs_hp, bs_hp_max), True, WHITE)
            screen.blit(txt_bs_hp, [10, 10])
            if bs_hp <= 0:
                boss.gekiha()
                idx = 6

        elif idx == 6:
            control()
            if tmr % 30 < 15:  # 主人公描画 15フレーム(0.5秒)ごとにアニメーション
                screen.blit(img_chara[0], [ch_x, ch_y])
            else:
                screen.blit(img_chara[1], [ch_x, ch_y])

            tama()
            tama_2()
            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            ii = 0
            idx = 1
            if level == MAX_LEVEL:
                idx = 7
            else:
                level = level + 1
                ch_hp = ch_hp_max
                pygame.mixer.init()
                se_gekiha = pygame.mixer.Sound("se\heel.ogg")
                se_gekiha.play()

        elif idx == 7: # クリア
            screen.blit(img_bg, [0, 0])  # 背景描画
            screen.blit(img_chara[0], [ch_x, ch_y])  # 描画
            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            bs_hp = 0
            if msbx == 0:
                msbx = 1
            elif msbx == 1:
                msbx = 2
                messagebox.showinfo("クリア！", "ゲームをクリアしました。OKを押してRキーでもう一回プレイできます。")

        elif idx == 8: #攻撃ターンとおしゃべりターンの切り替え
            ta_kakuritsu = 0
            screen.blit(img_bg, [0, 0])  # 背景描画
            bs_fight = 0
            control()

            if tmr % 30 < 15:  # 主人公描画 15フレーム(0.5秒)ごとにアニメーション
                screen.blit(img_chara[0], [ch_x, ch_y])
            else:
                screen.blit(img_chara[1], [ch_x, ch_y])
            
            tama()
            boss.sinariochu()
            

            txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
            screen.blit(txt_ch_hp, [10, 910])
            txt_bs_hp = font.render("BOSS HP:{}/{}".format(bs_hp, bs_hp_max), True, WHITE)
            screen.blit(txt_bs_hp, [10, 10])

            sinario_num = boss.si

            ii = ii + 1
            if ii == 60:
                ii = 0
                idx = 9
        elif idx == 9: #ボスが話す
            if is_press_enter == 1 and is_pull_enter == 1:
                sinario_num += 1
                ii += 1
                is_pull_enter = 0
            if ii == boss.sn-1:
                idx = 5
            else:
                font = pygame.font.Font(FONT_PATH, 50)
                ta_kakuritsu = 0
                screen.blit(img_bg, [0, 0])  # 背景描画
                bs_fight = 0
                
                if tmr % 30 < 15:  # 主人公描画 15フレーム(0.5秒)ごとにアニメーション
                    screen.blit(img_chara[0], [ch_x, ch_y])
                else:
                    screen.blit(img_chara[1], [ch_x, ch_y])

                tama()
                boss.sinariochu()

                txt_ch_hp = font.render("HP:{}/{}".format(ch_hp, ch_hp_max), True, WHITE)
                screen.blit(txt_ch_hp, [10, 910])
                txt_bs_hp = font.render("BOSS HP:{}/{}".format(bs_hp, bs_hp_max), True, WHITE)
                screen.blit(txt_bs_hp, [10, 10])

                
                screen.blit(img_tb, [60, 570])
                screen.blit(img_speaker[TXT_CHA[SINARIO[sinario_num][1]][1]], [90, 660])
                txt_name = font.render(TXT_CHA[SINARIO[sinario_num][1]][0], True, WHITE)
                screen.blit(txt_name, [124, 579])
                txt_main = font.render(SINARIO[sinario_num][0], True, WHITE)
                screen.blit(txt_main, [340, 660])

        pygame.display.update()
        clock.tick(30)


if __name__ == '__main__':
    main()
