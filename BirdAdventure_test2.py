import pygame
import sys
import random
import math
from tkinter import messagebox
import os # ファイルパス操作のため

# --- 基本設定 ---
screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("シューティング改 v1.2 (Debug Mode)") # タイトル変更

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0) # デバッグ表示用

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
        print(f"エラー: 画像ファイル '{path}' の読み込みに失敗しました。\n{e}")
        sys.exit()
    except FileNotFoundError:
        print(f"エラー: 画像ファイル '{path}' が見つかりません。'{img_dir}' フォルダを確認してください。")
        sys.exit()

# --- 画像読み込み ---
img_bg = load_image("bg_space.png")
img_tb = load_image("textbox.png")
img_chara = [
    load_image("ch_bird_1.png"),
    load_image("ch_bird_2.png"),
    load_image("ch_bird_died.png")
]
img_tama = load_image("tama.png")
img_tama_2 = load_image("tama_2.png")
img_boss = [load_image("boss_1.png")]
img_speaker = [load_image("sp_kari.png")]

# --- グローバル変数 ---
tmr = 0
idx = 0
ch_x = screen_width // 2 - img_chara[0].get_width() // 2
ch_y = screen_height - img_chara[0].get_height() - 50
ch_hp_max = 10
ch_hp = ch_hp_max
CH_SPD = 8
TA_MAX = 500
ta_x = [-100.0] * TA_MAX
ta_y = [-100.0] * TA_MAX
TA_SPD = 7
ta_kakuritsu = 1
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
MAX_LEVEL = 2
FONT_FILENAME = "ipaexg.ttf"
FONT_PATH = os.path.join(fnt_dir, FONT_FILENAME)

sinario_num = 0
is_press_enter = 0
is_pull_enter = 1

ta_utsu_Z = 0
ta_utsu_enter = 0

# --- デバッグ用フラグ --- ★★★ 追加
DEBUG_INFINITE_HP = False
DEBUG_INFINITE_ATK = False

# --- 効果音読み込みヘルパー ---
def load_sound(filename):
    path = os.path.join(se_dir, filename)
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except pygame.error as e:
        print(f"警告: 効果音ファイル '{path}' の読み込みに失敗しました。\n{e}")
        return None
    except FileNotFoundError:
        print(f"警告: 効果音ファイル '{path}' が見つかりません。'{se_dir}' フォルダを確認してください。")
        return None

# --- 効果音読み込み ---
pygame.mixer.init()
damage_sound = load_sound("damage_2.ogg")
shoot_sound = load_sound("hassha.ogg")
boss_damage_sound = load_sound("damage.ogg")
explosion_sound = load_sound("bakuhatsu.ogg")
heal_sound = load_sound("heel.ogg")

def play_sound(sound):
    if sound:
        sound.play()

# --- 関数定義 ---

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
    if new_x < 0: new_x = 0
    if new_x > screen_width - ch_img_w: new_x = screen_width - ch_img_w
    if new_y < 0: new_y = 0
    if new_y > screen_height - ch_img_h: new_y = screen_height - ch_img_h
    ch_x, ch_y = new_x, new_y

    ta_utsu_Z = key[pygame.K_z]
    ta_utsu_enter = key[pygame.K_RETURN]
    if ta_utsu_Z or ta_utsu_enter:
        if tmr % 5 == 1: ta_utsu = 1
        else: ta_utsu = 0
    else: ta_utsu = 0

def event():
    global idx, is_press_enter, is_pull_enter
    global DEBUG_INFINITE_HP, DEBUG_INFINITE_ATK # デバッグフラグをグローバル宣言 ★★★
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
            # --- デバッグキー処理 --- ★★★ 追加
            if event.key == pygame.K_F1:
                DEBUG_INFINITE_HP = not DEBUG_INFINITE_HP
                print(f"デバッグ: HP無限 = {DEBUG_INFINITE_HP}")
            if event.key == pygame.K_F2:
                DEBUG_INFINITE_ATK = not DEBUG_INFINITE_ATK
                print(f"デバッグ: 攻撃力無限 = {DEBUG_INFINITE_ATK}")
            # --- ここまで ---
        if event.type == pygame.KEYUP:
             if event.key == pygame.K_z or event.key == pygame.K_RETURN:
                 is_pull_enter = 1

def reset_game(): # 変更なし
    global idx, tmr, ch_x, ch_y, ch_hp, ta_x, ta_y, ta_2_x, ta_2_y, ta_kakudo, level, ii, bs_fight, msbx, sinario_num, is_pull_enter, boss, gmov
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

def tama():
    global ta_kakuritsu, gmov, idx, screen, ch_hp
    # HP無限フラグのチェックを最初に置く ★★★
    global DEBUG_INFINITE_HP
    t = 0
    active_bullets = 0

    ch_img_w = img_chara[0].get_width()
    ch_img_h = img_chara[0].get_height()
    tama_img_w = img_tama.get_width()
    tama_img_h = img_tama.get_height()
    ch_cx = ch_x + ch_img_w / 2
    ch_cy = ch_y + ch_img_h / 2
    ch_hit_radius_sq = (ATARIHANTEI_X + ATARIHANTEI_Y)**2 / 4

    for i in range(TA_MAX):
        if ta_y[i] > -100:
            active_bullets += 1
            rad = math.radians(ta_kakudo[i])
            ta_x[i] += TA_SPD * math.cos(rad)
            ta_y[i] += TA_SPD * math.sin(rad)

            if ta_y[i] > screen_height or ta_y[i] < -tama_img_h or ta_x[i] > screen_width or ta_x[i] < -tama_img_w:
                ta_y[i] = -100.0
            else:
                ta_cx = ta_x[i] + tama_img_w / 2
                ta_cy = ta_y[i] + tama_img_h / 2
                dist_sq = (ch_cx - ta_cx)**2 + (ch_cy - ta_cy)**2

                # 当たり判定とHP減少処理 ★★★ 修正
                if dist_sq < ch_hit_radius_sq:
                    if not DEBUG_INFINITE_HP: # HP無限でない場合のみダメージ処理
                        play_sound(damage_sound)
                        ch_hp -= 1
                        print(f"Hit! HP: {ch_hp}")
                        if ch_hp <= 0:
                            gmov = i
                            idx = 2
                    # HP無限でも弾は消す（当たりエフェクトなど出す場合は変更）
                    ta_y[i] = -100.0
                    if idx == 2 and not DEBUG_INFINITE_HP: # HP無限でなければゲームオーバーへ
                         break

                # 弾の描画 (当たり判定後、弾が消えていなければ) ★★★ 修正
                if ta_y[i] != -100.0:
                    try:
                        # 修正: さらに90度回転 ★★★
                        angle = -ta_kakudo[i] - 90
                        img_danmaku = pygame.transform.rotozoom(img_tama, angle, 1.0)
                        rect = img_danmaku.get_rect(center=(ta_cx, ta_cy))
                        screen.blit(img_danmaku, rect.topleft)
                    except Exception as e:
                        screen.blit(img_tama, [ta_x[i], ta_y[i]])

        # 通常弾生成 (変更なし)
        elif idx == 1 and bs_fight == 0:
             if t == 0:
                if random.randint(1, 1000) <= ta_kakuritsu:
                     for j in range(TA_MAX):
                         if ta_y[j] == -100.0:
                             ta_y[j] = -float(img_tama.get_height())
                             ta_x[j] = float(random.randint(0, screen_width - img_tama.get_width()))
                             ta_kakudo[j] = 90.0
                             t = 1
                             break

def tama_2():
    global ta_2_x, ta_2_y, TA_2_KAZU, ta_utsu, bs_hp
    global idx, screen, level, bs_fight, bs_x, bs_y
    # 攻撃力無限フラグのチェック ★★★
    global DEBUG_INFINITE_ATK

    tama2_img_w = img_tama_2.get_width()
    tama2_img_h = img_tama_2.get_height()
    ch_img_w = img_chara[0].get_width()

    # 新しい弾の発射処理 (変更なし)
    if ta_utsu == 1:
        for i in range(TA_2_KAZU):
            if ta_2_y[i] == -100.0:
                play_sound(shoot_sound)
                ta_2_y[i] = ch_y
                ta_2_x[i] = ch_x + ch_img_w / 2 - tama2_img_w / 2
                ta_utsu = 0
                break

    # 既存の弾の移動と描画、当たり判定
    for i in range(TA_2_KAZU):
        if ta_2_y[i] != -100.0:
            ta_2_y[i] -= TA_SPD * 1.5

            if ta_2_y[i] < -tama2_img_h:
                ta_2_y[i] = -100.0
            else:
                # ボスとの当たり判定 ★★★ 修正
                if bs_fight == 1 and Boss.current_boss and bs_hp > 0:
                    boss = Boss.current_boss
                    boss_rect = pygame.Rect(bs_x, bs_y, boss.sx, boss.sy)
                    tama_rect = pygame.Rect(ta_2_x[i], ta_2_y[i], tama2_img_w, tama2_img_h)

                    if boss_rect.colliderect(tama_rect):
                        if DEBUG_INFINITE_ATK: # 攻撃力無限ならボスHPを0に
                            bs_hp = 0
                            print("DEBUG: Boss HP set to 0 by Infinite Attack")
                        else: # 通常ダメージ
                            play_sound(boss_damage_sound)
                            bs_hp -= 1
                            # print(f"Boss Hit! HP: {bs_hp}")
                        ta_2_y[i] = -100.0 # 弾は消す

                # 画面に描画 (変更なし)
                if ta_2_y[i] != -100.0:
                    screen.blit(img_tama_2, [ta_2_x[i], ta_2_y[i]])

# --- Bossクラス定義 (変更なし) ---
class Boss:
    current_boss = None

    def __init__(self, id, hp, size_x, size_y, sinario_ichi, sinario_nagasa, img_index=0):
        self.id = id
        self.hp = hp
        self.max_hp = hp
        self.sx = size_x
        self.sy = size_y
        self.si = sinario_ichi
        self.sn = sinario_nagasa
        self.img_index = img_index
        if self.img_index >= len(img_boss):
            self.img_index = 0
        self.img = img_boss[self.img_index]
        self.attack_pattern_timer = 0
        self.move_target_x = float(screen_width // 2 - self.sx // 2)
        self.move_target_y = 50.0
        self.is_moving = False

    def rdy(self, progress):
        global bs_x, bs_y, bs_hp, bs_hp_max
        bs_x = float(screen_width // 2 - self.sx // 2)
        final_y = 50.0
        start_y = -float(self.sy)
        bs_y = start_y + (final_y - start_y) * progress
        bs_hp = self.hp
        bs_hp_max = self.max_hp
        screen.blit(self.img, [bs_x, bs_y])

    def sinariochu(self):
        global bs_x, bs_y
        bs_x = float(screen_width // 2 - self.sx // 2)
        bs_y = 50.0
        screen.blit(self.img, [bs_x, bs_y])

    def gekiha(self):
        play_sound(explosion_sound)

    def move(self):
        global bs_x, bs_y
        speed = 4.0
        dx = self.move_target_x - bs_x
        dy = self.move_target_y - bs_y
        dist = math.sqrt(dx**2 + dy**2)

        if dist < speed:
            bs_x = self.move_target_x
            bs_y = self.move_target_y
            self.is_moving = False
        elif dist > 0:
            bs_x += dx / dist * speed
            bs_y += dy / dist * speed
            self.is_moving = True

        if not self.is_moving:
            if random.randint(1, 120) <= BS_UGOKUHINDO:
                self.move_target_x = float(random.randint(0, screen_width - self.sx))
                self.move_target_y = float(random.randint(20, 200))
                self.is_moving = True

    def _find_available_bullet(self):
        for i in range(TA_MAX):
            idx_to_check = (ta_num + i) % TA_MAX
            if ta_y[idx_to_check] == -100.0:
                return idx_to_check
        return None

    def _fire_bullet(self, angle, offset_x=0, offset_y=0):
        global ta_num
        bullet_idx = self._find_available_bullet()
        if bullet_idx is not None:
            fire_x = bs_x + self.sx / 2 + offset_x
            fire_y = bs_y + self.sy / 2 + offset_y
            ta_x[bullet_idx] = fire_x - img_tama.get_width() / 2
            ta_y[bullet_idx] = fire_y - img_tama.get_height() / 2
            ta_kakudo[bullet_idx] = angle % 360
            ta_num = (bullet_idx + 1) % TA_MAX
            return True
        return False

    def attack(self):
        global bs_x, bs_y, ch_x, ch_y
        self.move()
        self.attack_pattern_timer += 1
        screen.blit(self.img, [bs_x, bs_y])
        boss_cx = bs_x + self.sx / 2
        boss_cy = bs_y + self.sy / 2

        if self.id == 1:
            fire_interval1 = 50
            if self.attack_pattern_timer % fire_interval1 == 1:
                num_bullets = 16
                angle_step = 360 / num_bullets
                start_angle = (self.attack_pattern_timer // fire_interval1) * 7
                for i in range(num_bullets):
                    angle = start_angle + i * angle_step
                    self._fire_bullet(angle)

            fire_interval2 = 65
            if self.attack_pattern_timer % fire_interval2 == 15:
                player_cx = ch_x + img_chara[0].get_width() / 2
                player_cy = ch_y + img_chara[0].get_height() / 2
                dx = player_cx - boss_cx
                dy = player_cy - boss_cy
                base_angle = math.degrees(math.atan2(dy, dx))
                spread = 12
                for i in range(-1, 2):
                    angle = base_angle + i * spread
                    self._fire_bullet(angle)

        elif self.id == 2:
            fire_interval1 = 22
            if self.attack_pattern_timer % fire_interval1 == 1:
                 ways = 6
                 angle_step = 360 / ways
                 base_angle = (self.attack_pattern_timer * 2.5) % 360
                 for i in range(ways):
                     angle = base_angle + i * angle_step
                     self._fire_bullet(angle)

            fire_interval2 = 6
            shots_per_burst = 4
            burst_interval = 70
            if self.attack_pattern_timer % burst_interval < fire_interval2 * shots_per_burst and \
               self.attack_pattern_timer % fire_interval2 == 1 :
                 angle = random.uniform(0, 360)
                 self._fire_bullet(angle)

            fire_interval3 = 100
            if self.attack_pattern_timer % fire_interval3 == 40:
                 player_cx = ch_x + img_chara[0].get_width() / 2
                 player_cy = ch_y + img_chara[0].get_height() / 2
                 dx = player_cx - boss_cx
                 dy = player_cy - boss_cy
                 angle = math.degrees(math.atan2(dy, dx))
                 self._fire_bullet(angle)


# --- メインループ ---
def main():
    global tmr, idx, screen, ii, level, boss
    global ch_x, ch_y, CH_SPD, ch_hp, ch_hp_max
    global TA_MAX, ta_x, ta_y, TA_SPD, ta_kakuritsu, ta_num
    global ta_2_x, ta_2_y, TA_2_KAZU, ta_utsu
    global gmov, msbx, ATARIHANTEI_X, ATARIHANTEI_Y
    global bs_x, bs_y, bs_fight, bs_hp, bs_hp_max
    global sinario_num, is_press_enter, is_pull_enter, FONT_PATH
    # デバッグフラグをmainからも参照 ★★★
    global DEBUG_INFINITE_HP, DEBUG_INFINITE_ATK

    pygame.init()
    clock = pygame.time.Clock()

    # フォント設定 (前回と同様)
    font_hp = None
    font_talk = None
    font_debug = None # デバッグ表示用フォント ★★★
    font_size_hp = 36
    font_size_talk = 42
    font_size_debug = 24 # デバッグ表示用フォントサイズ ★★★

    try:
        font_hp = pygame.font.Font(FONT_PATH, font_size_hp)
        font_talk = pygame.font.Font(FONT_PATH, font_size_talk)
        font_debug = pygame.font.Font(FONT_PATH, font_size_debug) # ★★★
        print("カスタムフォントのロード成功。")
    except Exception as e: # エラーの種類を広くキャッチ
        print(f"警告: カスタムフォント '{FONT_PATH}' の読み込みに失敗。エラー: {e}")

    if font_hp is None or font_talk is None or font_debug is None:
        print("システムフォントでの代替を試みます...")
        system_fonts = ["Meiryo", "Yu Gothic", "MS Gothic", "TakaoGothic", "Hiragino Sans GB", "Arial Unicode MS"]
        found_sys_font = False
        for font_name in system_fonts:
            try:
                if font_hp is None: font_hp = pygame.font.SysFont(font_name, font_size_hp)
                if font_talk is None: font_talk = pygame.font.SysFont(font_name, font_size_talk)
                if font_debug is None: font_debug = pygame.font.SysFont(font_name, font_size_debug) # ★★★
                print(f"システムフォント '{font_name}' のロード成功。")
                found_sys_font = True
                break
            except Exception: # エラーの種類を広くキャッチ
                 pass # 次のフォントを試す

        if not found_sys_font:
            print("警告: 日本語対応のシステムフォントが見つかりませんでした。デフォルトフォントを使用します。")
            try:
                if font_hp is None: font_hp = pygame.font.Font(None, 45)
                if font_talk is None: font_talk = pygame.font.Font(None, 55)
                if font_debug is None: font_debug = pygame.font.Font(None, 30) # ★★★
            except pygame.error as e:
                print(f"致命的エラー: デフォルトフォントの読み込みにも失敗しました: {e}")
                pygame.quit()
                sys.exit()

    boss = None
    reset_game()

    while True:
        tmr += 1
        event()
        control()

        screen.blit(img_bg, [0, 0])

        # --- idxによる状態分岐 (内容はほぼ変更なし) ---
        if idx == 0:
            level = 1
            tmr = 0
            ii = 0
            bs_fight = 0
            ta_kakuritsu = 8
            ch_hp = ch_hp_max
            idx = 1

        elif idx == 1:
            ii += 1
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], [ch_x, ch_y])
            tama()
            tama_2()
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # Bossへ
            boss_appear_time = 120
            if ii >= boss_appear_time: idx = 3; ii = 0

        elif idx == 2:
            screen.blit(img_chara[2], [ch_x, ch_y])
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # UI Boss HP
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, [10, 10])
            # Msg Box
            if msbx == 0: msbx = 1
            elif msbx == 1:
                messagebox.showinfo("ゲームオーバー！", "弾に当たってしまいました。\nOKを押した後、Rキーでもう一回プレイできます。")
                msbx = 2

        elif idx == 3:
            ta_kakuritsu = 0; bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], [ch_x, ch_y])
            tama(); tama_2() # 描画のみ
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # Boss生成
            if boss is None or boss.id != level:
                if level == 1: boss = Boss(1, 800, 300, 200, 0, 5)
                elif level == 2: boss = Boss(2, 1400, 300, 200, 7, 3)
                else: idx = 7; continue
                if boss: Boss.current_boss = boss; print(f"Level {level} Boss generated."); ii = 0; idx = 4
            else: idx = 4

        elif idx == 4:
            ta_kakuritsu = 0; bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], [ch_x, ch_y])
            tama(); tama_2() # 描画のみ
            # Boss登場演出
            appear_duration = 60
            if ii < appear_duration:
                progress = ii / appear_duration
                boss.rdy(progress); ii += 1
                hp_bar_base_y = 10
                hp_bar_y = -30 + (hp_bar_base_y + 30) * progress
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, [10, hp_bar_y])
            else:
                boss.rdy(1.0)
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, [10, 10])
                idx = 8; ii = 0
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])

        elif idx == 5: # ボス戦
            ta_kakuritsu = 0; bs_fight = 1
            if boss: boss.attack()
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], [ch_x, ch_y])
            tama(); tama_2()
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # UI Boss HP & Bar
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                text_width = txt_bs_hp.get_width()
                screen.blit(txt_bs_hp, [10, 10])
                hp_ratio = max(0, bs_hp / bs_hp_max)
                bar_width = 300; bar_height = 15
                bar_x = 10 + text_width + 10
                bar_y = 10 + (font_size_hp - bar_height) // 2
                pygame.draw.rect(screen, GRAY, [bar_x, bar_y, bar_width, bar_height])
                pygame.draw.rect(screen, RED, [bar_x, bar_y, bar_width * hp_ratio, bar_height])
            # Boss撃破判定
            if bs_hp <= 0 and bs_hp_max > 0:
                bs_hp_max = 0; bs_fight = 0
                if boss: boss.gekiha()
                idx = 6; ii = 0

        elif idx == 6: # ボス撃破後
            bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], [ch_x, ch_y])
            tama(); tama_2() # 残弾処理
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # 次へ
            clear_wait_time = 90
            if ii < clear_wait_time: ii += 1
            else:
                level += 1
                if level > MAX_LEVEL: idx = 7 # クリア
                else:
                    play_sound(heal_sound); ch_hp = ch_hp_max
                    ta_x = [-100.0] * TA_MAX; ta_y = [-100.0] * TA_MAX
                    ta_2_x = [-100.0] * TA_2_KAZU; ta_2_y = [-100.0] * TA_2_KAZU
                    boss = None; Boss.current_boss = None
                    idx = 1; ii = 0

        elif idx == 7: # クリア
            screen.blit(img_chara[0], [ch_x, ch_y])
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # Clear Text
            clear_text = font_talk.render("Game Clear!", True, WHITE)
            clear_rect = clear_text.get_rect(center=(screen_width/2, screen_height/2))
            screen.blit(clear_text, clear_rect)
            # Msg Box
            if msbx == 0: msbx = 1
            elif msbx == 1:
                messagebox.showinfo("クリア！", "ゲームをクリアしました。\nOKを押した後、Rキーでもう一回プレイできます。")
                msbx = 2

        elif idx == 8: # 会話準備
            ta_kakuritsu = 0; bs_fight = 0
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], [ch_x, ch_y])
            tama() # 描画のみ
            if boss: boss.sinariochu()
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # UI Boss HP
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, [10, 10])
            # Scenario設定
            if boss: sinario_num = boss.si
            else: idx = 5; continue
            # 会話へ
            wait_frames = 30
            if tmr % (wait_frames * 2) == wait_frames: idx = 9

        elif idx == 9: # 会話シーン
            ta_kakuritsu = 0; bs_fight = 0
            if is_press_enter == 1: sinario_num += 1; is_press_enter = 0
            # Scenario終了判定
            if boss and sinario_num >= boss.si + boss.sn:
                idx = 5;
                if boss: boss.attack_pattern_timer = 0
                continue
            elif not boss: idx = 1; continue
            # 描画
            anim_frame = (tmr // 15) % 2
            screen.blit(img_chara[anim_frame], [ch_x, ch_y])
            tama()
            if boss: boss.sinariochu()
            # UI HP
            txt_ch_hp = font_hp.render(f"HP:{ch_hp}/{ch_hp_max}", True, WHITE)
            screen.blit(txt_ch_hp, [10, screen_height - font_size_hp - 10])
            # UI Boss HP
            if bs_hp_max > 0:
                txt_bs_hp = font_hp.render(f"BOSS HP:{bs_hp}/{bs_hp_max}", True, WHITE)
                screen.blit(txt_bs_hp, [10, 10])
            # Text Box
            try:
                current_sinario = SINARIO[sinario_num]
                serifu = current_sinario[0]; char_id = current_sinario[1]
                char_info = TXT_CHA[char_id]; char_name = char_info[0]; speaker_img_idx = char_info[1]
                tb_h = img_tb.get_height(); tb_x = 60; tb_y = screen_height - tb_h - 20
                screen.blit(img_tb, [tb_x, tb_y])
                # Speaker Img
                if speaker_img_idx < len(img_speaker):
                    sp_img = img_speaker[speaker_img_idx]
                    sp_x = tb_x + 30; sp_y = tb_y + (tb_h - sp_img.get_height()) // 2
                    screen.blit(sp_img, [sp_x, sp_y])
                    speaker_area_width = sp_img.get_width() + 30
                else: sp_x = tb_x; speaker_area_width = 0
                # Name
                name_x = sp_x + speaker_area_width + 10; name_y = tb_y + 15
                txt_name = font_talk.render(char_name, True, WHITE)
                screen.blit(txt_name, [name_x, name_y])
                # Serifu
                main_x = name_x; main_y = name_y + font_talk.get_height() + 5
                txt_main = font_talk.render(serifu, True, WHITE)
                screen.blit(txt_main, [main_x, main_y])
                # Next Indicator
                if tmr % 40 < 20:
                     next_indicator = font_talk.render("▼", True, WHITE)
                     indicator_x = tb_x + img_tb.get_width() - 60
                     indicator_y = tb_y + tb_h - 50
                     screen.blit(next_indicator, (indicator_x, indicator_y))
            except Exception as e:
                print(f"エラー: 会話描画 {e}"); idx = 5
                if boss: boss.attack_pattern_timer = 0

        # --- デバッグ情報描画 --- ★★★ 追加
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
        # --- ここまで ---

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()
