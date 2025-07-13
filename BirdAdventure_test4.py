# -*- coding: utf-8 -*-
import pygame
import sys
import random
import math
from tkinter import messagebox # メッセージボックス用 (代替推奨)
import os

# --- 基本設定 ---
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("シューティング改 v1.6 (Syntax Fix)") # タイトル変更

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# --- ディレクトリ設定 ---
img_dir = "img"
se_dir = "se"
fnt_dir = "fnt"

# --- 画像読み込みヘルパー ---
def load_image(filename):
    path = os.path.join(img_dir, filename)
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"エラー: 画像 '{path}' 失敗: {e}")
        sys.exit()
    except FileNotFoundError:
        print(f"エラー: 画像 '{path}' なし")
        sys.exit()

# --- 画像読み込み ---
img_bg = load_image("bg_space.png")
img_tb = load_image("textbox.png")
img_chara = [ load_image("ch_bird_1.png"), load_image("ch_bird_2.png"), load_image("ch_bird_died.png") ]
img_tama = load_image("tama.png")
img_tama_2 = load_image("tama_2.png")
img_boss = [load_image("boss_1.png")]
img_speaker = [load_image("sp_kari.png")]

# 雑魚敵用画像（主人公画像を縮小）
zako_scale = 0.4
try:
    img_zako_orig = img_chara[0]
    img_zako = pygame.transform.smoothscale(img_zako_orig,
                                    (int(img_zako_orig.get_width() * zako_scale),
                                     int(img_zako_orig.get_height() * zako_scale)))
except pygame.error as e:
    print(f"警告: 雑魚敵画像の縮小に失敗しました: {e}。代わりに弾画像を使用します。")
    img_zako = pygame.transform.rotozoom(img_tama, 180, 1.2)


# --- グローバル変数 ---
tmr = 0
idx = 0
ch_x = screen_width // 2 - img_chara[0].get_width() // 2
ch_y = screen_height - img_chara[0].get_height() - 50
ch_hp_max = 10
ch_hp = ch_hp_max
CH_SPD = 8
TA_MAX = 750
ta_x = [-100.0] * TA_MAX
ta_y = [-100.0] * TA_MAX
TA_SPD = 7
ta_kakudo = [270.0] * TA_MAX
ta_num = 0
TA_2_KAZU = 200
ta_2_x = [-100.0] * TA_2_KAZU
ta_2_y = [-100.0] * TA_2_KAZU
ta_utsu = 0
gmov = -1
msbx = 0
ATARIHANTEI_X = 18
ATARIHANTEI_Y = 22
bs_x = 0.0
bs_y = 0.0
BS_UGOKUHINDO = 3
bs_hp = 0
bs_hp_max = 0
bs_fight = 0
level = 0
ii = 0
MAX_LEVEL = 4
FONT_FILENAME = "ipaexg.ttf"
FONT_PATH = os.path.join(fnt_dir, FONT_FILENAME)
sinario_num = 0
is_press_enter = 0
is_pull_enter = 1
ta_utsu_Z = 0
ta_utsu_enter = 0

# デバッグ用フラグ
DEBUG_INFINITE_HP = False
DEBUG_INFINITE_ATK = False

# 雑魚敵関連
zakos = []
ZAKO_HP_DEFAULT = 2
ZAKO_FIRE_INTERVAL = 110

# --- テキストデータ (変更なし) ---
TXT_CHA = [ ["鳥", 0] ]
SINARIO = [
    # L1
    ["やあ。僕は鳥だよ。", 0], ["鳥は種類だろだって?", 0], ["違う。", 0],
    ["種類が鳥なんじゃなくて名前が鳥。", 0], ["まあ細かいことはいい。小手調べといこうか！", 0], # [4]
    # Unused
    ["なかなかやるじゃないか。", 0], ["だが、これで終わりではないぞ！", 0], # [5][6]
    # L2
    ["ふむ、ここまで来るとはな。", 0], ["少しは楽しませてくれそうだ。", 0],
    ["私の本気を見せてやろう！", 0], # [9]
    # L3
    ["ほう…私の本気すら超えるか。", 0], ["面白い！ 実に面白いぞ、挑戦者！", 0],
    ["だが、遊びはここまでだ。", 0], ["この宇宙の深淵を見せてやろう！　覚悟！！", 0], # [13]
    # L4
    ["な、なんだと…！？ この私が…！", 0], # [14] L4 シナリオ開始位置
    ["許さん…許さんぞぉぉぉ！", 0],
    ["もはや手加減はせん！ 真の絶望を味わうがいいッ！！", 0], # [16] L4 シナリオ長さ = 3
]

# --- 効果音読み込み (変更なし) ---
def load_sound(filename):
    path = os.path.join(se_dir, filename)
    try:
        return pygame.mixer.Sound(path)
    except pygame.error as e:
        print(f"警告: 効果音 '{path}' 失敗: {e}")
        return None
    except FileNotFoundError:
        print(f"警告: 効果音 '{path}' なし")
        return None

pygame.mixer.init()
damage_sound = load_sound("damage_2.ogg")
shoot_sound = load_sound("hassha.ogg")
boss_damage_sound = load_sound("damage.ogg")
explosion_sound = load_sound("bakuhatsu.ogg")
heal_sound = load_sound("heel.ogg")
zako_damage_sound = load_sound("damage.ogg")
zako_destroy_sound = load_sound("bakuhatsu.ogg")

def play_sound(sound):
    if sound:
        sound.play()

# --- 汎用関数 (変更なし) ---
def find_available_bullet_index():
    for i in range(TA_MAX):
        if ta_y[i] == -100.0:
            return i
    return None

def fire_enemy_bullet(x, y, angle):
    idx = find_available_bullet_index()
    if idx is not None:
        ta_x[idx] = x - img_tama.get_width() / 2
        ta_y[idx] = y - img_tama.get_height() / 2
        ta_kakudo[idx] = angle % 360
        return True
    return False

# --- 雑魚敵クラス (変更なし) ---
class Zako:
    def __init__(self, x, y, hp=ZAKO_HP_DEFAULT, type=0, speed=3.0):
        self.x = float(x)
        self.y = float(y)
        self.hp = hp
        self.max_hp = hp
        self.type = type
        self.speed = float(speed)
        self.img = img_zako
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.timer = 0
        self.fire_timer = random.randint(0, ZAKO_FIRE_INTERVAL // 2)

    def move_pattern_1(self):
        self.y += self.speed

    def update(self):
        self.timer += 1
        self.fire_timer += 1
        self.move_pattern_1()

        if self.y > screen_height + self.height or self.x < -self.width or self.x > screen_width:
            self.hp = 0
            return

        if self.fire_timer >= ZAKO_FIRE_INTERVAL:
            self.fire()
            self.fire_timer = 0

        screen.blit(self.img, (self.x, self.y))

    def fire(self):
        fire_x = self.x + self.width / 2
        fire_y = self.y + self.height
        fire_enemy_bullet(fire_x, fire_y, 90.0)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            play_sound(zako_destroy_sound)
            return True
        else:
            play_sound(zako_damage_sound)
            return False

# --- 雑魚敵生成関数 (変更なし) ---
def spawn_zako(current_time):
    if level == 1:
        if current_time % 120 == 60:
            zakos.append(Zako(100, -img_zako.get_height()))
            zakos.append(Zako(screen_width - 100 - img_zako.get_width(), -img_zako.get_height()))
        if current_time % 200 == 150:
             center_x = screen_width // 2 - img_zako.get_width() // 2
             zakos.append(Zako(center_x - 80, -img_zako.get_height()))
             zakos.append(Zako(center_x, -img_zako.get_height()-40))
             zakos.append(Zako(center_x + 80, -img_zako.get_height()))
    elif level == 2:
        if current_time % 100 == 40:
            zakos.append(Zako(200, -img_zako.get_height(), hp=ZAKO_HP_DEFAULT+1, speed=3.5))
            zakos.append(Zako(screen_width - 200 - img_zako.get_width(), -img_zako.get_height(), hp=ZAKO_HP_DEFAULT+1, speed=3.5))
        if current_time % 180 == 100:
            for i in range(5):
                 x_pos = (screen_width / 6)*(i+1)-img_zako.get_width()/2
                 zakos.append(Zako(x_pos, -img_zako.get_height()-i*15, hp=ZAKO_HP_DEFAULT, speed=3.0))
    elif level == 3:
         if current_time % 90 == 30:
             zakos.append(Zako(50, -img_zako.get_height(), hp=ZAKO_HP_DEFAULT+2, speed=4.0))
             zakos.append(Zako(screen_width - 50 - img_zako.get_width(), -img_zako.get_height(), hp=ZAKO_HP_DEFAULT+2, speed=4.0))
         if current_time % 150 == 80:
              for i in range(4):
                   x_pos = random.randint(50, screen_width - 50 - img_zako.get_width())
                   zakos.append(Zako(x_pos, -img_zako.get_height()-i*20, hp=ZAKO_HP_DEFAULT+1, speed=3.5))

# --- 雑魚敵更新・描画関数 (変更なし) ---
def update_zakos():
    global zakos
    for i in range(len(zakos) - 1, -1, -1):
        zako = zakos[i]
        zako.update()
        if zako.hp <= 0:
            del zakos[i]

# --- 既存関数 (control, event, reset_game は変更なし、tama, tama_2 は微修正) ---
def control(): # 変更なし
    global ch_x, ch_y, ta_utsu, ta_utsu_Z, ta_utsu_enter
    key = pygame.key.get_pressed()
    new_x, new_y = ch_x, ch_y
    if key[pygame.K_UP]:
        new_y -= CH_SPD
    if key[pygame.K_DOWN]:
        new_y += CH_SPD
    if key[pygame.K_LEFT]:
        new_x -= CH_SPD
    if key[pygame.K_RIGHT]:
        new_x += CH_SPD
    ch_img_w = img_chara[0].get_width()
    ch_img_h = img_chara[0].get_height()
    if new_x < 0:
        new_x = 0
    if new_x > screen_width - ch_img_w:
        new_x = screen_width - ch_img_w
    if new_y < 0:
        new_y = 0
    if new_y > screen_height - ch_img_h:
        new_y = screen_height - ch_img_h
    ch_x, ch_y = new_x, new_y
    ta_utsu_Z = key[pygame.K_z]
    ta_utsu_enter = key[pygame.K_RETURN]
    if ta_utsu_Z or ta_utsu_enter:
        if tmr % 5 == 1:
            ta_utsu = 1
        else:
            ta_utsu = 0
    else:
        ta_utsu = 0

def event(): # 変更なし
    global idx, is_press_enter, is_pull_enter, DEBUG_INFINITE_HP, DEBUG_INFINITE_ATK
    is_press_enter = 0
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                if is_pull_enter == 1:
                    is_press_enter = 1
                    is_pull_enter = 0
            if event.key == pygame.K_F1:
                DEBUG_INFINITE_HP = not DEBUG_INFINITE_HP
                print(f"DEBUG: HP Inf = {DEBUG_INFINITE_HP}")
            if event.key == pygame.K_F2:
                DEBUG_INFINITE_ATK = not DEBUG_INFINITE_ATK
                print(f"DEBUG: ATK Inf = {DEBUG_INFINITE_ATK}")
        if event.type == pygame.KEYUP:
             if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                 is_pull_enter = 1

def reset_game(): # 変更なし
    global idx, tmr, ch_x, ch_y, ch_hp, ta_x, ta_y, ta_2_x, ta_2_y, ta_kakudo, level, ii, bs_fight, msbx, sinario_num, is_pull_enter, boss, gmov, zakos
    idx = 0
    tmr = 0
    ch_x = screen_width // 2 - img_chara[0].get_width() // 2
    ch_y = screen_height - img_chara[0].get_height() - 50
    ch_hp = ch_hp_max
    ta_x = [-100.0] * TA_MAX
    ta_y = [-100.0] * TA_MAX
    ta_2_x = [-100.0] * TA_2_KAZU
    ta_2_y = [-100.0] * TA_2_KAZU
    ta_kakudo = [270.0] * TA_MAX
    level = 0
    ii = 0
    bs_fight = 0
    msbx = 0
    sinario_num = 0
    is_pull_enter = 1
    boss = None
    Boss.current_boss = None
    gmov = -1
    zakos = []

def tama(): # 敵弾処理 (変更なし、向き修正済み)
    global gmov, idx, screen, ch_hp, DEBUG_INFINITE_HP
    ch_img_w = img_chara[0].get_width()
    ch_img_h = img_chara[0].get_height()
    tama_img_w = img_tama.get_width()
    tama_img_h = img_tama.get_height()
    ch_cx = ch_x + ch_img_w / 2
    ch_cy = ch_y + ch_img_h / 2
    ch_hit_radius_sq = (ATARIHANTEI_X + ATARIHANTEI_Y)**2 / 4

    for i in range(TA_MAX):
        if ta_y[i] > -100:
            rad = math.radians(ta_kakudo[i])
            ta_x[i] += TA_SPD * math.cos(rad)
            ta_y[i] += TA_SPD * math.sin(rad)

            if ta_y[i] > screen_height or ta_y[i] < -tama_img_h or ta_x[i] > screen_width or ta_x[i] < -tama_img_w:
                ta_y[i] = -100.0
            else:
                ta_cx = ta_x[i] + tama_img_w / 2
                ta_cy = ta_y[i] + tama_img_h / 2
                dist_sq = (ch_cx - ta_cx)**2 + (ch_cy - ta_cy)**2

                if dist_sq < ch_hit_radius_sq:
                    if not DEBUG_INFINITE_HP:
                        play_sound(damage_sound)
                        ch_hp -= 1
                        print(f"Hit! HP: {ch_hp}")
                        if ch_hp <= 0:
                            gmov = i
                            idx = 2
                    ta_y[i] = -100.0 # HP無限でも弾は消す
                    if idx == 2 and not DEBUG_INFINITE_HP:
                        break # ゲームオーバーならループ抜ける

                if ta_y[i] != -100.0: # 弾が有効なら描画
                    try:
                        angle = 270.0 - ta_kakudo[i] # 向き修正済み
                        img_danmaku = pygame.transform.rotozoom(img_tama, angle, 1.0)
                        rect = img_danmaku.get_rect(center=(ta_cx, ta_cy))
                        screen.blit(img_danmaku, rect.topleft)
                    except Exception: # Fallback drawing
                        screen.blit(img_tama, (ta_x[i], ta_y[i]))
    # ランダム弾生成は停止中

def tama_2(): # 自機弾処理 (変更なし)
    global ta_2_x, ta_2_y, ta_utsu, bs_hp, DEBUG_INFINITE_ATK, zakos
    tama2_img_w = img_tama_2.get_width()
    tama2_img_h = img_tama_2.get_height()
    ch_img_w = img_chara[0].get_width()

    if ta_utsu == 1:
        for i in range(TA_2_KAZU):
            if ta_2_y[i] == -100.0:
                play_sound(shoot_sound)
                ta_utsu = 0
                ta_2_y[i] = ch_y
                ta_2_x[i] = ch_x + ch_img_w / 2 - tama2_img_w / 2
                break

    for i in range(TA_2_KAZU):
        if ta_2_y[i] != -100.0:
            ta_2_y[i] -= TA_SPD * 1.5
            if ta_2_y[i] < -tama2_img_h:
                ta_2_y[i] = -100.0
            else:
                tama_rect = pygame.Rect(ta_2_x[i], ta_2_y[i], tama2_img_w, tama2_img_h)
                hit_target = False

                if bs_fight == 1 and Boss.current_boss and bs_hp > 0:
                    boss = Boss.current_boss
                    boss_rect = pygame.Rect(bs_x, bs_y, boss.sx, boss.sy)
                    if boss_rect.colliderect(tama_rect):
                        hit_target = True
                        if DEBUG_INFINITE_ATK:
                            bs_hp = 0
                            print("DEBUG: Boss HP 0")
                        else:
                            play_sound(boss_damage_sound)
                            bs_hp -= 1
                        ta_2_y[i] = -100.0

                if not hit_target and idx == 1:
                    for j in range(len(zakos) - 1, -1, -1):
                        # リスト範囲チェックを追加（安全のため）
                        if j < len(zakos):
                            zako = zakos[j]
                            zako_rect = pygame.Rect(zako.x, zako.y, zako.width, zako.height)
                            if zako_rect.colliderect(tama_rect):
                                hit_target = True
                                destroyed = zako.take_damage(1)
                                ta_2_y[i] = -100.0
                                break # 1弾1ヒット

                if ta_2_y[i] != -100.0:
                    screen.blit(img_tama_2, (ta_2_x[i], ta_2_y[i]))

class Boss: # Bossクラス (変更なし)
    current_boss = None
    def __init__(self, id, hp, size_x, size_y, sinario_ichi, sinario_nagasa, img_index=0):
        self.id=id; self.hp=hp; self.max_hp=hp; self.sx=size_x; self.sy=size_y
        self.si=sinario_ichi; self.sn=sinario_nagasa; self.img_index=img_index
        if self.img_index >= len(img_boss): self.img_index = 0
        self.img=img_boss[self.img_index]; self.attack_pattern_timer=0
        self.move_target_x = float(screen_width//2-self.sx//2); self.move_target_y=50.0; self.is_moving=False
    def rdy(self, progress):
        global bs_x, bs_y, bs_hp, bs_hp_max
        bs_x=float(screen_width//2-self.sx//2); final_y=50.0; start_y=-float(self.sy)
        bs_y=start_y+(final_y-start_y)*progress; bs_hp=self.hp; bs_hp_max=self.max_hp
        screen.blit(self.img, (bs_x, bs_y))
    def sinariochu(self):
        global bs_x, bs_y; bs_x=float(screen_width//2-self.sx//2); bs_y=50.0
        screen.blit(self.img, (bs_x, bs_y))
    def gekiha(self): play_sound(explosion_sound)
    def move(self):
        global bs_x, bs_y; speed=4.0; dx=self.move_target_x-bs_x; dy=self.move_target_y-bs_y; dist=math.sqrt(dx**2+dy**2)
        if dist<speed: bs_x=self.move_target_x; bs_y=self.move_target_y; self.is_moving=False
        elif dist>0: bs_x+=dx/dist*speed; bs_y+=dy/dist*speed; self.is_moving=True
        if not self.is_moving:
            if random.randint(1, 120)<=BS_UGOKUHINDO:
                self.move_target_x=float(random.randint(0, screen_width-self.sx))
                self.move_target_y=float(random.randint(20, 200)); self.is_moving=True
    def _find_available_bullet(self):
        for i in range(TA_MAX):
            idx_to_check=(ta_num+i)%TA_MAX
            if ta_y[idx_to_check]==-100.0:
                return idx_to_check
        return None
    def _fire_bullet(self, angle, offset_x=0, offset_y=0, speed_mult=1.0):
        global ta_num; bullet_idx=self._find_available_bullet()
        if bullet_idx is not None:
            fire_x=bs_x+self.sx/2+offset_x; fire_y=bs_y+self.sy/2+offset_y
            ta_x[bullet_idx]=fire_x-img_tama.get_width()/2; ta_y[bullet_idx]=fire_y-img_tama.get_height()/2
            ta_kakudo[bullet_idx]=angle%360; ta_num=(bullet_idx+1)%TA_MAX; return True
        return False
    def attack(self): # 変更なし (id=4パターン含む)
        global bs_x, bs_y, ch_x, ch_y; self.move(); self.attack_pattern_timer+=1; screen.blit(self.img, (bs_x, bs_y))
        boss_cx=bs_x+self.sx/2; boss_cy=bs_y+self.sy/2; player_cx=ch_x+img_chara[0].get_width()/2; player_cy=ch_y+img_chara[0].get_height()/2
        if self.id==1:
            fire_interval1=50
            if self.attack_pattern_timer%fire_interval1==1: num_bullets=16; angle_step=360/num_bullets; start_angle=(self.attack_pattern_timer//fire_interval1)*7; [self._fire_bullet(start_angle+i*angle_step) for i in range(num_bullets)]
            fire_interval2=65
            if self.attack_pattern_timer%fire_interval2==15: dx=player_cx-boss_cx; dy=player_cy-boss_cy; base_angle=math.degrees(math.atan2(dy, dx)); spread=12; [self._fire_bullet(base_angle+i*spread) for i in range(-1, 2)]
        elif self.id==2:
            fire_interval1=22
            if self.attack_pattern_timer%fire_interval1==1: ways=6; angle_step=360/ways; base_angle=(self.attack_pattern_timer*2.5)%360; [self._fire_bullet(base_angle+i*angle_step) for i in range(ways)]
            fire_interval2=6; shots_per_burst=4; burst_interval=70
            if self.attack_pattern_timer%burst_interval<fire_interval2*shots_per_burst and self.attack_pattern_timer%fire_interval2==1: self._fire_bullet(random.uniform(0, 360))
            fire_interval3=100
            if self.attack_pattern_timer%fire_interval3==40: dx=player_cx-boss_cx; dy=player_cy-boss_cy; angle=math.degrees(math.atan2(dy, dx)); self._fire_bullet(angle)
        elif self.id==3:
            fire_interval1=35
            if self.attack_pattern_timer%fire_interval1==1: num_bullets=24; angle_step=360/num_bullets; start_angle=(self.attack_pattern_timer//fire_interval1)*11; [self._fire_bullet(start_angle+i*angle_step) for i in range(num_bullets)]
            fire_interval2=50
            if self.attack_pattern_timer%fire_interval2==10: dx=player_cx-boss_cx; dy=player_cy-boss_cy; base_angle=math.degrees(math.atan2(dy, dx)); spread=10; [self._fire_bullet(base_angle+i*spread) for i in range(-2, 3)]; [self._fire_bullet(random.uniform(0, 360)) for _ in range(4)]
            fire_interval3=120
            if self.attack_pattern_timer%fire_interval3==60: num_laser=3; [fire_enemy_bullet((screen_width/(num_laser+1))*(i+1), -img_tama.get_height(), 90.0) for i in range(num_laser)]
            fire_interval4=25
            if self.attack_pattern_timer%fire_interval4==5: ways=8; angle_step=360/ways; base_angle1=(self.attack_pattern_timer*3.0)%360; base_angle2=(-self.attack_pattern_timer*2.5)%360; [self._fire_bullet(base_angle1+i*angle_step) for i in range(ways)]; [self._fire_bullet(base_angle2+i*angle_step+angle_step/2) for i in range(ways)]
        elif self.id == 4:
            fire_interval1 = 8; amp = 45; freq = 4
            if self.attack_pattern_timer % fire_interval1 == 1:
                t_rad = math.radians(self.attack_pattern_timer * freq)
                angle_L = 15 + amp * math.sin(t_rad); self._fire_bullet(angle_L, offset_x = -self.sx * 0.45)
                angle_R = 165 - amp * math.sin(t_rad); self._fire_bullet(angle_R, offset_x = self.sx * 0.45)
            fire_interval2 = 75
            if self.attack_pattern_timer % fire_interval2 == 25:
                num_bullets = 24; angle_step = 360 / num_bullets
                radius = 60 + 50 * math.sin(math.radians(self.attack_pattern_timer * 2.0))
                for i in range(num_bullets):
                    angle = i * angle_step; rad = math.radians(angle)
                    offset_x = radius * math.cos(rad); offset_y = radius * math.sin(rad)
                    self._fire_bullet(angle, offset_x=offset_x, offset_y=offset_y)
            fire_interval3 = 55
            if self.attack_pattern_timer % fire_interval3 == 0:
                dx=player_cx-boss_cx; dy=player_cy-boss_cy; base_angle=math.degrees(math.atan2(dy, dx)); spread=18
                for i in range(-1, 2): self._fire_bullet(base_angle + i * spread)
                for _ in range(8): self._fire_bullet(random.uniform(base_angle - 60, base_angle + 60))
            fire_interval4 = 130
            if self.attack_pattern_timer % fire_interval4 == 70:
                 wall_margin = 20; num_streams = 3
                 for i in range(num_streams):
                     for j in range(4):
                         t_offset = j * 2
                         if self.attack_pattern_timer + t_offset > tmr:
                             y_pos1 = screen_height * (i+1) / (num_streams + 1) - j*5
                             y_pos2 = screen_height * (i+1) / (num_streams + 1) + j*5
                             x_pos1 = screen_width * (i+1) / (num_streams + 1) - j*5
                             x_pos2 = screen_width * (i+1) / (num_streams + 1) + j*5
                             fire_enemy_bullet(wall_margin, y_pos1, 0.0)
                             fire_enemy_bullet(screen_width - wall_margin, y_pos2, 180.0)
                             fire_enemy_bullet(x_pos1, wall_margin, 90.0)
                             fire_enemy_bullet(x_pos2, screen_height - wall_margin - img_tama.get_height(), 270.0)

# --- メインループ ---
def main():
    global tmr, idx, screen, ii, level, boss, zakos, ch_x, ch_y, ch_hp, ch_hp_max
    global bs_fight, bs_hp, bs_hp_max, DEBUG_INFINITE_HP, DEBUG_INFINITE_ATK
    global is_press_enter, sinario_num # グローバル変数を参照

    pygame.init()
    clock = pygame.time.Clock()

    # フォント設定 (変更なし)
    font_hp = None; font_talk = None; font_debug = None
    font_size_hp = 36; font_size_talk = 42; font_size_debug = 24
    try: font_hp = pygame.font.Font(FONT_PATH, font_size_hp); font_talk = pygame.font.Font(FONT_PATH, font_size_talk); font_debug = pygame.font.Font(FONT_PATH, font_size_debug); print("カスタムフォント成功")
    except Exception as e: print(f"カスタムフォント失敗: {e}")
    if font_hp is None or font_talk is None or font_debug is None:
        print("システムフォント代替試行..."); system_fonts = ["Meiryo", "Yu Gothic", "MS Gothic", "TakaoGothic", "Hiragino Sans GB", "Arial Unicode MS"]; found_sys_font = False
        for font_name in system_fonts:
            try:
                if font_hp is None: font_hp = pygame.font.SysFont(font_name, font_size_hp)
                if font_talk is None: font_talk = pygame.font.SysFont(font_name, font_size_talk)
                if font_debug is None: font_debug = pygame.font.SysFont(font_name, font_size_debug)
                print(f"システムフォント '{font_name}' 成功"); found_sys_font = True; break
            except Exception: pass
        if not found_sys_font:
            print("警告: 日本語システムフォント見つからず。デフォルトフォント使用。")
            try:
                if font_hp is None: font_hp = pygame.font.Font(None, 45)
                if font_talk is None: font_talk = pygame.font.Font(None, 55)
                if font_debug is None: font_debug = pygame.font.Font(None, 30)
            except pygame.error as e: print(f"致命的エラー: デフォルトフォント失敗: {e}"); pygame.quit(); sys.exit()

    boss = None
    reset_game()

    while True:
        tmr += 1
        event()
        control()
        screen.blit(img_bg, (0, 0)) # 各フレームの最初に背景描画

        # --- idxによる状態分岐 ---
        if idx == 0:
            level = 1
            tmr = 0
            ii = 0
            bs_fight = 0
            ch_hp = ch_hp_max
            idx = 1

        elif idx == 1: # 通常プレイ (雑魚戦)
            ii += 1
            spawn_zako(ii)
            update_zakos() # 雑魚更新・描画含む
            tama()         # 敵弾更新・描画含む
            tama_2()       # 自機弾更新・描画含む

            # 自機描画
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], (ch_x, ch_y))

            # UI描画
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))
            level_text = font_hp.render(f"Level {level}", True, WHITE)
            screen.blit(level_text, (screen_width - level_text.get_width() - 10, 10))

            # ボス戦移行判定
            boss_appear_time = 1500 # 通常プレイ時間
            if ii >= boss_appear_time:
                idx = 3
                ii = 0
                zakos = [] # ボス戦前に雑魚クリア

        elif idx == 2: # ゲームオーバー
            screen.blit(img_chara[2], (ch_x, ch_y))
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, (10, 10))
            if msbx == 0:
                msbx = 1
            elif msbx == 1:
                messagebox.showinfo("ゲームオーバー！", "弾に当たってしまいました。\nOKを押した後、Rキーでもう一回プレイできます。")
                msbx = 2

        elif idx == 3: # ボス準備
            bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], (ch_x, ch_y))
            tama() # 残弾描画
            tama_2() # 残弾描画
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))

            # ボス生成
            if boss is None or boss.id != level:
                if   level == 1: boss = Boss(1, 800, 300, 200, 0, 5)
                elif level == 2: boss = Boss(2, 1400, 300, 200, 7, 3)
                elif level == 3: boss = Boss(3, 2200, 300, 200, 10, 4)
                elif level == 4: boss = Boss(4, 3000, 300, 200, 14, 3)
                else:
                    idx = 7 # クリア
                    continue
                if boss:
                    Boss.current_boss = boss
                    print(f"Level {level} Boss generated.")
                    ii = 0
                    idx = 4
            else:
                idx = 4 # リトライ時など

        elif idx == 4: # ボス登場
            bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], (ch_x, ch_y))
            tama()
            tama_2()
            appear_duration = 60
            if ii < appear_duration:
                progress = ii / appear_duration
                boss.rdy(progress)
                ii += 1
                hp_bar_base_y = 10
                hp_bar_y = -30 + (hp_bar_base_y + 30) * progress
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, (10, hp_bar_y))
            else:
                boss.rdy(1.0)
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, (10, 10))
                idx = 8 # 会話へ
                ii = 0 # 会話待機用にリセット
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))

        elif idx == 5: # ボス戦
            bs_fight = 1
            if boss:
                boss.attack()
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], (ch_x, ch_y))
            tama()
            tama_2()
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                text_width = txt_bs_hp.get_width()
                screen.blit(txt_bs_hp, (10, 10))
                hp_ratio = max(0, bs_hp / bs_hp_max)
                bar_width = 300
                bar_height = 15
                bar_x = 10 + text_width + 10
                bar_y = 10 + (font_size_hp - bar_height) // 2
                pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width * hp_ratio, bar_height))
            if bs_hp <= 0 and bs_hp_max > 0:
                bs_hp_max = 0 # 1回だけ処理
                bs_fight = 0
                if boss:
                    boss.gekiha()
                idx = 6
                ii = 0

        elif idx == 6: # ボス撃破後
            bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], (ch_x, ch_y))
            tama()
            tama_2()
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))
            clear_wait_time = 90
            if ii < clear_wait_time:
                ii += 1
            else:
                level += 1
                if level > MAX_LEVEL:
                    idx = 7 # クリア
                else:
                    play_sound(heal_sound)
                    ch_hp = ch_hp_max
                    # 弾と雑魚をクリア
                    ta_x = [-100.0] * TA_MAX
                    ta_y = [-100.0] * TA_MAX
                    ta_2_x = [-100.0] * TA_2_KAZU
                    ta_2_y = [-100.0] * TA_2_KAZU
                    zakos = []
                    boss = None
                    Boss.current_boss = None
                    idx = 1 # 次のレベルへ
                    ii = 0

        elif idx == 7: # クリア
            screen.blit(img_chara[0], (ch_x, ch_y))
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))
            clear_text = font_talk.render("Game Clear!", True, WHITE)
            clear_rect = clear_text.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(clear_text, clear_rect)
            if msbx == 0:
                msbx = 1
            elif msbx == 1:
                messagebox.showinfo("クリア！", "ゲームをクリアしました。\nOKを押した後、Rキーでもう一回プレイできます。")
                msbx = 2

        elif idx == 8: # 会話準備
            bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], (ch_x, ch_y))
            tama() # 残弾描画
            if boss:
                boss.sinariochu()
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, (10, 10))
            if boss:
                sinario_num = boss.si
            else: # ボスがいない場合は戦闘へ（エラー回避）
                idx = 5
                continue
            wait_frames = 30
            ii += 1 # 会話開始までの待機タイマー
            if ii >= wait_frames :
                idx = 9
                ii = 0 # 会話シーン用にリセット

        elif idx == 9: # 会話シーン
            bs_fight = 0
            # is_press_enter は event() で更新される
            if is_press_enter == 1:
                sinario_num += 1
                # is_press_enter は次のフレームでリセットされる

            # シナリオ終了判定
            if boss and sinario_num >= boss.si + boss.sn:
                idx = 5 # ボス戦へ
                if boss:
                    boss.attack_pattern_timer = 0 # ボス攻撃タイマーリセット
                continue # 次のループへ
            elif not boss: # ボスがいない場合 (通常は起こらないはず)
                idx = 1
                continue

            # 描画
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], (ch_x, ch_y))
            tama()
            if boss:
                boss.sinariochu()
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, (10, screen_height - font_size_hp - 10))
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, (10, 10))

            # テキストボックス描画
            try:
                current_sinario = SINARIO[sinario_num]
                serifu = current_sinario[0]
                char_id = current_sinario[1]
                char_info = TXT_CHA[char_id]
                char_name = char_info[0]
                speaker_img_idx = char_info[1]
                tb_h = img_tb.get_height()
                tb_x = 60
                tb_y = screen_height - tb_h - 20
                screen.blit(img_tb, (tb_x, tb_y))
                # 話者画像
                if speaker_img_idx < len(img_speaker):
                    sp_img = img_speaker[speaker_img_idx]
                    sp_x = tb_x + 30
                    sp_y = tb_y + (tb_h - sp_img.get_height()) // 2
                    screen.blit(sp_img, (sp_x, sp_y))
                    speaker_area_width = sp_img.get_width() + 30
                else:
                    sp_x = tb_x
                    speaker_area_width = 0
                # 名前とセリフ
                name_x = sp_x + speaker_area_width + 10
                name_y = tb_y + 15
                txt_name = font_talk.render(char_name, True, WHITE)
                screen.blit(txt_name, (name_x, name_y))
                main_x = name_x
                main_y = name_y + font_talk.get_height() + 5
                txt_main = font_talk.render(serifu, True, WHITE)
                screen.blit(txt_main, (main_x, main_y))
                # 次へ送るインジケータ
                if tmr % 40 < 20:
                     next_indicator = font_talk.render("▼", True, WHITE)
                     indicator_x = tb_x + img_tb.get_width() - 60
                     indicator_y = tb_y + tb_h - 50
                     screen.blit(next_indicator, (indicator_x, indicator_y))
            except Exception as e:
                print(f"エラー: 会話描画 {e}")
                idx = 5 # エラー時は戦闘へ
                if boss:
                    boss.attack_pattern_timer = 0

        # --- デバッグ情報描画 ---
        if font_debug:
            debug_texts = []
            if DEBUG_INFINITE_HP:
                debug_texts.append("HP Inf (F1)")
            if DEBUG_INFINITE_ATK:
                debug_texts.append("ATK Inf (F2)")
            if debug_texts:
                full_debug_text = "DEBUG: " + " / ".join(debug_texts)
                debug_surf = font_debug.render(full_debug_text, True, YELLOW)
                debug_rect = debug_surf.get_rect(bottomright=(screen_width - 10, screen_height - 10))
                screen.blit(debug_surf, debug_rect)

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()
