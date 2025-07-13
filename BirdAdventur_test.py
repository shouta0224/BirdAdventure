# 必要なライブラリをインポート
import pygame as pg
import sys
import random as rd
import math
from tkinter import messagebox as mbx

# --- 初期設定 ---
pg.init()
pg.mixer.init()  # Mixerを早期に初期化
screen_width, screen_height = 1280, 960
s = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("最適化シューティング")
clk = pg.time.Clock()
WHITE = (255, 255, 255)

# --- 画像読み込み ---
# エラーハンドリングを追加
def load_image(path):
    try:
        return pg.image.load(path)
    except pg.error as e:
        print(f"画像読み込みエラー: {path} - {e}")
        mbx.showerror("エラー", f"画像ファイルの読み込みに失敗しました:\n{path}\n{e}")
        pg.quit(); sys.exit()
    except FileNotFoundError as e:
        print(f"画像ファイルが見つかりません: {path} - {e}")
        mbx.showerror("エラー", f"画像ファイルが見つかりません:\n{path}")
        pg.quit(); sys.exit()


img_bg = load_image("img/bg_space.png")
img_tb = load_image("img/textbox.png")
img_ch = [
    load_image("img/ch_bird_1.png"),
    load_image("img/ch_bird_2.png"),
    load_image("img/ch_bird_died.png")
]
img_tama_enemy = load_image("img/tama.png")
img_tama_player = load_image("img/tama_2.png")
img_boss = [load_image("img/boss_1.png")]
img_speaker = [load_image("img/sp_kari.png")]

# --- 効果音読み込み ---
def load_sound(path):
    try:
        return pg.mixer.Sound(path)
    except pg.error as e:
        print(f"効果音読み込みエラー: {path} - {e}")
        # mbx.showwarning("警告", f"効果音ファイルの読み込みに失敗しました:\n{path}\n{e}") # 必要なら警告
        return None # 効果音なしで続行
    except FileNotFoundError as e:
        print(f"効果音ファイルが見つかりません: {path} - {e}")
        return None

se_damage_player = load_sound("se/damage_2.ogg") # プレイヤー被弾
se_damage_boss = load_sound("se/damage.ogg")     # ボス被弾
se_shoot_player = load_sound("se/hassha.ogg")    # プレイヤー発射
se_boss_defeated = load_sound("se/bakuhatsu.ogg")# ボス撃破
se_level_up = load_sound("se/heel.ogg")          # レベルアップ回復

# --- フォント設定 ---
FONT_PATH = "fnt/ipaexg.ttf"
try:
    font_main = pg.font.Font(None, 60)         # UI用
    font_scenario = pg.font.Font(FONT_PATH, 50) # 会話用
except pg.error as e:
    print(f"フォント読み込みエラー: {FONT_PATH} - {e}")
    font_main = pg.font.Font(None, 60) # デフォルトで代替
    font_scenario = pg.font.Font(None, 50)
    mbx.showwarning("警告", f"フォント読み込みに失敗。デフォルトフォントを使用します:\n{e}")
except FileNotFoundError as e:
     print(f"フォントファイルが見つかりません: {FONT_PATH} - {e}")
     font_main = pg.font.Font(None, 60) # デフォルトで代替
     font_scenario = pg.font.Font(None, 50)
     mbx.showwarning("警告", f"指定フォントが見つかりません。デフォルトフォントを使用します:\n{e}")


# --- ゲーム定数 ---
CH_SPEED = 10
TAMA_ENEMY_MAX = 300
TAMA_ENEMY_SPEED = 10
TAMA_PLAYER_MAX = 200
TAMA_PLAYER_SPEED = 15 # プレイヤーの弾速を少し上げる
TAMA_PLAYER_INTERVAL = 4 # 発射間隔フレーム (小さいほど速い)
HIT_RADIUS_X = 25
HIT_RADIUS_Y = 30
BOSS_MOVE_FREQ = 2
MAX_LEVEL = 1

# --- ゲーム変数 ---
tmr = 0         # グローバルタイマー
idx = 0         # ゲーム状態インデックス
ch_x = screen_width // 2 - img_ch[0].get_width() // 2  # 中央下部に初期配置
ch_y = screen_height - img_ch[0].get_height() - 50
ch_hp_max = 10
ch_hp = ch_hp_max
shoot_timer = 0 # プレイヤー弾発射用タイマー
key_shoot_pressed = False # 射撃キーが押されているか
key_enter_pressed_event = False # Enter/Zが押されたフレームか (イベント処理用)

# 敵弾リスト (x, y, angle)
tama_enemy = [[-100, -100, 270] for _ in range(TAMA_ENEMY_MAX)]
tama_enemy_spawn_idx = 0 # ボス弾用

# プレイヤー弾リスト (x, y) - 角度は常に上(-90度)
tama_player = [[-100, -100] for _ in range(TAMA_PLAYER_MAX)]

game_over_bullet_idx = 0 # ゲームオーバー原因の弾
message_box_shown = False

# ボス関連
bs_x = 0
bs_y = 0
bs_hp = 0
bs_hp_max = 0
bs_fighting = False
current_boss = None

level = 0
scene_timer = 0 # 各シーンの内部タイマー
scenario_idx = 0 # 現在のシナリオ番号

# テキストデータ
TXT_CHARS = [["鳥", 0]]
SCENARIO = [
    ["やあ。僕は鳥だよ。", 0],
    ["鳥は種類だろだって?", 0],
    ["違う。", 0],
    ["種類が鳥なんじゃなくて名前が鳥。", 0],
    ["よし、いくぞ！", 0] # 最後のセリフを修正
]

# --- 関数定義 ---

def control_player():
    """プレイヤーの移動と射撃キーの状態を処理"""
    global ch_x, ch_y, key_shoot_pressed
    keys = pg.key.get_pressed()
    if keys[pg.K_UP]:    ch_y = max(0, ch_y - CH_SPEED)
    if keys[pg.K_DOWN]:  ch_y = min(screen_height - img_ch[0].get_height(), ch_y + CH_SPEED)
    if keys[pg.K_LEFT]:  ch_x = max(0, ch_x - CH_SPEED)
    if keys[pg.K_RIGHT]: ch_x = min(screen_width - img_ch[0].get_width(), ch_x + CH_SPEED)
    key_shoot_pressed = keys[pg.K_z] or keys[pg.K_RETURN]

def handle_events():
    """ゲームイベント（終了、リセット、会話送り）を処理"""
    global idx, key_enter_pressed_event
    key_enter_pressed_event = False # フレーム開始時にリセット
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                idx = 0 # ゲームリセット
            # ZキーまたはEnterキーが押された瞬間だけフラグを立てる
            if event.key == pg.K_z or event.key == pg.K_RETURN:
                key_enter_pressed_event = True

def process_enemy_bullets():
    """敵弾の移動、画面外判定、当たり判定、描画"""
    global ch_hp, idx, game_over_bullet_idx
    for i in range(TAMA_ENEMY_MAX):
        if tama_enemy[i][1] > -100: # 弾が有効か
            angle_rad = math.radians(tama_enemy[i][2])
            tama_enemy[i][0] += TAMA_ENEMY_SPEED * math.cos(angle_rad)
            tama_enemy[i][1] += TAMA_ENEMY_SPEED * math.sin(angle_rad)

            # 画面外判定
            if tama_enemy[i][1] > screen_height or tama_enemy[i][0] < -50 or tama_enemy[i][0] > screen_width + 50:
                tama_enemy[i][1] = -100 # 無効化
                continue

            # プレイヤーとの当たり判定 (中心座標で比較、少し甘めに)
            ch_center_x = ch_x + img_ch[0].get_width() / 2
            ch_center_y = ch_y + img_ch[0].get_height() / 2
            tama_center_x = tama_enemy[i][0] + img_tama_enemy.get_width() / 2
            tama_center_y = tama_enemy[i][1] + img_tama_enemy.get_height() / 2

            if abs(ch_center_x - tama_center_x) < HIT_RADIUS_X and \
               abs(ch_center_y - tama_center_y) < HIT_RADIUS_Y:
                if se_damage_player: se_damage_player.play()
                ch_hp -= 1
                tama_enemy[i][1] = -100 # 弾消滅
                if ch_hp <= 0:
                    game_over_bullet_idx = i
                    idx = 2 # ゲームオーバー状態へ
                continue # 当たったら描画しない

            # 描画
            rotated_bullet = pg.transform.rotozoom(img_tama_enemy, 90 - tama_enemy[i][2], 1.0)
            s.blit(rotated_bullet, (tama_enemy[i][0], tama_enemy[i][1]))

def process_player_bullets():
    """プレイヤー弾の生成、移動、画面外判定、当たり判定、描画"""
    global shoot_timer, bs_hp
    shoot_timer += 1

    # 弾の発射 (キーが押され、発射間隔を満たした場合)
    if key_shoot_pressed and shoot_timer >= TAMA_PLAYER_INTERVAL:
        shoot_timer = 0 # タイマーリセット
        # 未使用の弾を探して発射
        for i in range(TAMA_PLAYER_MAX):
            if tama_player[i][1] == -100:
                if se_shoot_player: se_shoot_player.play()
                tama_player[i][0] = ch_x + img_ch[0].get_width() / 2 - img_tama_player.get_width() / 2
                tama_player[i][1] = ch_y # 自機の上端から
                break # 1フレーム1発まで

    # 弾の移動と当たり判定
    for i in range(TAMA_PLAYER_MAX):
        if tama_player[i][1] > -100: # 弾が有効か
            tama_player[i][1] -= TAMA_PLAYER_SPEED # 上へ移動

            # 画面外判定
            if tama_player[i][1] < -img_tama_player.get_height():
                tama_player[i][1] = -100 # 無効化
                continue

            # ボスとの当たり判定
            if bs_fighting and bs_hp > 0 and current_boss:
                # ボスの当たり判定矩形 (Bossクラスに持たせるべき)
                boss_rect = pg.Rect(bs_x, bs_y, current_boss.sx, current_boss.sy)
                bullet_rect = pg.Rect(tama_player[i][0], tama_player[i][1], img_tama_player.get_width(), img_tama_player.get_height())

                if boss_rect.colliderect(bullet_rect):
                    if se_damage_boss: se_damage_boss.play()
                    bs_hp -= 1
                    tama_player[i][1] = -100 # 弾消滅
                    continue # 当たったら描画しない

            # 描画
            s.blit(img_tama_player, (tama_player[i][0], tama_player[i][1]))

class Boss:
    """ボスクラス"""
    def __init__(self, id, hp, size_x, size_y, talk_start_idx, talk_length):
        self.id = id
        self.hp = hp
        self.sx = size_x
        self.sy = size_y
        self.talk_start = talk_start_idx
        self.talk_len = talk_length
        self.img = img_boss[id - 1] if 0 <= id - 1 < len(img_boss) else None
        if not self.img:
            print(f"警告: Boss ID {id} の画像が見つかりません")

    def set_pos(self, x, y):
        """ボスの位置を設定し、グローバル変数も更新"""
        global bs_x, bs_y
        bs_x, bs_y = x, y

    def appear(self, current_y):
        """登場演出中のボス位置設定と描画"""
        global bs_hp, bs_hp_max
        self.set_pos(screen_width / 2 - self.sx / 2, current_y)
        bs_hp, bs_hp_max = self.hp, self.hp # HPも設定
        if self.img: s.blit(self.img, (bs_x, bs_y))

    def set_pos_talk(self):
        """会話中のボス位置設定と描画"""
        self.set_pos(screen_width / 2 - self.sx / 2, 50) # 画面上部に固定
        if self.img: s.blit(self.img, (bs_x, bs_y))

    def defeated_sound(self):
        """撃破音再生"""
        if se_boss_defeated: se_boss_defeated.play()

    def attack(self):
        """ボスの攻撃パターン"""
        global tama_enemy_spawn_idx

        # 移動
        if rd.randint(1, 100) <= BOSS_MOVE_FREQ:
            target_x = rd.randint(50, screen_width - self.sx - 50)
            target_y = rd.randint(50, screen_height // 3) # 画面上半分程度
            # Lerpで滑らかに移動 (オプション)
            self.set_pos(bs_x + (target_x - bs_x) * 0.1, bs_y + (target_y - bs_y) * 0.1)
        else:
             self.set_pos(bs_x, bs_y) # 移動しない場合も位置を更新


        # 弾発射 (全方位弾) - 発射頻度を調整
        if rd.randint(1, 30) == 1: # 発射確率
            num_bullets = 18 # 発射する弾数
            angle_step = 360 / num_bullets
            start_angle = rd.uniform(0, angle_step) # 開始角度をランダムに
            spawn_x = bs_x + self.sx / 2
            spawn_y = bs_y + self.sy / 2
            for i in range(num_bullets):
                # 未使用の弾を探す (インデックスを回す)
                found_slot = False
                for _ in range(TAMA_ENEMY_MAX): # 無限ループ防止
                    if tama_enemy[tama_enemy_spawn_idx][1] == -100:
                         found_slot = True
                         break
                    tama_enemy_spawn_idx = (tama_enemy_spawn_idx + 1) % TAMA_ENEMY_MAX
                if found_slot:
                    angle = start_angle + i * angle_step
                    tama_enemy[tama_enemy_spawn_idx][0] = spawn_x
                    tama_enemy[tama_enemy_spawn_idx][1] = spawn_y
                    tama_enemy[tama_enemy_spawn_idx][2] = angle
                else:
                    print("警告：敵弾のスロットが不足しています")
                    break # 弾が満杯なら中断

        if self.img: s.blit(self.img, (bs_x, bs_y))

def draw_ui():
    """HPなどのUIを描画"""
    hp_text = font_main.render(f"HP: {ch_hp}/{ch_hp_max}", True, WHITE)
    s.blit(hp_text, (10, screen_height - hp_text.get_height() - 10))
    if bs_fighting or idx in [4, 8, 9]: # ボス出現中 or 戦闘中 or 会話中
        boss_hp_text = font_main.render(f"BOSS HP: {max(0, bs_hp)}/{bs_hp_max}", True, WHITE)
        s.blit(boss_hp_text, (10, 10))

def draw_scenario():
    """会話シーンの描画"""
    if not current_boss or not (0 <= scenario_idx < len(SCENARIO)):
        return

    s.blit(img_tb, (60, screen_height - img_tb.get_height() - 40)) # テキストボックス位置調整

    char_data_idx = SCENARIO[scenario_idx][1]
    if 0 <= char_data_idx < len(TXT_CHARS):
        char_name = TXT_CHARS[char_data_idx][0]
        speaker_img_idx = TXT_CHARS[char_data_idx][1]

        # 話者名
        name_surf = font_scenario.render(char_name, True, WHITE)
        s.blit(name_surf, (124, screen_height - img_tb.get_height() - 31)) # 名前位置調整

        # 話者画像
        if 0 <= speaker_img_idx < len(img_speaker):
             speaker_img = img_speaker[speaker_img_idx]
             s.blit(speaker_img, (90, screen_height - img_tb.get_height() + 50 )) # 画像位置調整
        else: print(f"警告: 話者画像インデックス不正 {speaker_img_idx}")

    else: print(f"警告: キャラクターデータインデックス不正 {char_data_idx}")

    # セリフ
    line_surf = font_scenario.render(SCENARIO[scenario_idx][0], True, WHITE)
    s.blit(line_surf, (340, screen_height - img_tb.get_height() + 50)) # セリフ位置調整

# --- メインループ ---
while True:
    tmr += 1
    handle_events() # イベント取得を先に行う
    control_player() # プレイヤー操作

    # 背景描画
    s.blit(img_bg, (0, 0))

    # 状態に応じた処理
    if idx == 0: # 初期化
        idx = 1
        ch_x = screen_width // 2 - img_ch[0].get_width() // 2
        ch_y = screen_height - img_ch[0].get_height() - 50
        ch_hp = ch_hp_max
        # 弾リストをクリア
        tama_enemy = [[-100, -100, 270] for _ in range(TAMA_ENEMY_MAX)]
        tama_player = [[-100, -100] for _ in range(TAMA_PLAYER_MAX)]
        message_box_shown = False
        level = 1 # 開始レベル
        tmr = 0
        scene_timer = 0
        bs_fighting = False
        current_boss = None

    elif idx == 1: # 通常ステージ (ボス前)
        scene_timer += 1
        bs_fighting = False; bs_hp = 0 # ボス情報はクリア
        # process_enemy_bullets() # 通常ステージ用の敵弾処理 (今回はボスのみ)
        process_player_bullets()
        s.blit(img_ch[0 if tmr % 30 < 15 else 1], (ch_x, ch_y)) # 自機アニメーション
        # 一定時間経過でボス準備へ
        if scene_timer >= 120: # 少し時間を延ばす
            idx = 3

    elif idx == 2: # ゲームオーバー
        s.blit(img_ch[2], (ch_x, ch_y)) # 被弾自機
        # 原因の弾を描画 (もし有効なら)
        if 0 <= game_over_bullet_idx < TAMA_ENEMY_MAX and tama_enemy[game_over_bullet_idx][1] > -100:
            b_x, b_y, b_angle = tama_enemy[game_over_bullet_idx]
            rotated_bullet = pg.transform.rotozoom(img_tama_enemy, 90 - b_angle, 1.0)
            s.blit(rotated_bullet, (b_x, b_y))
        # メッセージボックス表示 (一度だけ)
        if not message_box_shown:
            message_box_shown = True
            mbx.showinfo("ゲームオーバー！", "弾に当たりました。\nRキーでリトライ。")

    elif idx == 3: # ボス準備
        bs_fighting = False
        process_player_bullets() # 準備中も撃てる
        s.blit(img_ch[0 if tmr % 30 < 15 else 1], (ch_x, ch_y))
        if level == 1: # レベルに応じたボス生成
             current_boss = Boss(1, 200, 300, 200, 0, len(SCENARIO)) # HP増加, 会話長をSCENARIOに合わせる
        if current_boss:
             scene_timer = 0
             idx = 4 # 登場演出へ
        else:
             print("エラー：現在のレベルに対応するボスがいません。クリア扱いにします。")
             idx = 7 # ボスがいない場合はクリア

    elif idx == 4: # ボス登場演出
        bs_fighting = False
        process_player_bullets()
        s.blit(img_ch[0 if tmr % 30 < 15 else 1], (ch_x, ch_y))
        # ボスを画面上端からゆっくり降ろす
        appear_y = -current_boss.sy + (current_boss.sy + 50) * (scene_timer / 60) # 60フレームかけて登場
        current_boss.appear(min(50, appear_y)) # 最終Y座標を50に

        scene_timer += 1
        if scene_timer >= 60: # 登場完了
            scene_timer = 0
            idx = 8 # 会話前準備へ

    elif idx == 5: # ボス戦
        bs_fighting = True
        if current_boss: current_boss.attack() # ボス攻撃処理と描画
        process_enemy_bullets() # 敵弾処理
        process_player_bullets() # 自機弾処理と描画
        s.blit(img_ch[0 if tmr % 30 < 15 else 1], (ch_x, ch_y)) # 自機描画
        if bs_hp <= 0: # ボス撃破
            if current_boss: current_boss.defeated_sound()
            # 敵弾を消す
            tama_enemy = [[-100, -100, 270] for _ in range(TAMA_ENEMY_MAX)]
            idx = 6

    elif idx == 6: # ボス撃破後処理
        bs_fighting = False; bs_hp = 0
        process_player_bullets() # 残った自機弾の処理
        s.blit(img_ch[0 if tmr % 30 < 15 else 1], (ch_x, ch_y))
        scene_timer += 1
        # 撃破後、少し待ってから次へ
        if scene_timer >= 90:
            scene_timer = 0
            if level == MAX_LEVEL:
                idx = 7 # クリア
            else:
                level += 1
                ch_hp = ch_hp_max # HP回復
                if se_level_up: se_level_up.play()
                idx = 1 # 次のステージへ (現状はループ)

    elif idx == 7: # クリア
        bs_fighting = False; bs_hp = 0
        s.blit(img_ch[0], (ch_x, ch_y)) # 通常自機
        if not message_box_shown:
            message_box_shown = True
            mbx.showinfo("クリア！", "ゲームクリア！\nRキーでリトライ。")

    elif idx == 8: # 会話前準備
        bs_fighting = False
        # process_player_bullets() # 撃てても良い
        if current_boss: current_boss.set_pos_talk() # ボスを会話位置へ配置・描画
        s.blit(img_ch[0 if tmr % 30 < 15 else 1], (ch_x, ch_y))
        scene_timer += 1
        if scene_timer >= 60: # 少し待って会話へ
            scene_timer = 0
            scenario_idx = current_boss.talk_start if current_boss else 0
            idx = 9

    elif idx == 9: # 会話シーン
        bs_fighting = False
        if current_boss: current_boss.set_pos_talk() # ボス描画
        s.blit(img_ch[0 if tmr % 30 < 15 else 1], (ch_x, ch_y)) # 自機描画

        # 会話送り処理 (キーが押された瞬間のみ)
        if key_enter_pressed_event:
            scenario_idx += 1
            # 会話終了判定
            if not current_boss or scenario_idx >= current_boss.talk_start + current_boss.talk_len:
                idx = 5 # 会話終了、ボス戦へ

        # シナリオ描画 (idxが5に遷移する前に描画)
        if idx == 9:
             draw_scenario()


    # --- 共通処理 ---
    draw_ui() # UI描画

    # 画面更新とフレームレート制御
    pg.display.update()
    clk.tick(60) # フレームレート60FPS
