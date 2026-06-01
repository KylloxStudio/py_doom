import math
from resources import Resources

class Game:
    SCREEN_WIDTH  = 1280
    SCREEN_HEIGHT = 720
    
    WINDOW_WIDTH  = 1280
    WINDOW_HEIGHT = 720
    
    SCREEN_WIDTH_HALF  = SCREEN_WIDTH // 2
    SCREEN_HEIGHT_HALF = SCREEN_HEIGHT // 2

    FRAME_RATE = 60
    
    SCORE_TIME = 0.1
    

class State:
    MAIN = 'main'
    INGAME = 'ingame'
    PAUSED = 'paused'
    GAMEOVER = 'gameover'
    

class Sound:
    import sys
    
    _is_web = sys.platform == "emscripten"
    
    HIT_PATH = Resources.get_path("sounds/hit.ogg" if _is_web else "sounds/hit.mp3")
    HIT_VOLUME = 0.04
    
    KILL_PATH = Resources.get_path("sounds/kill.ogg" if _is_web else "sounds/kill.mp3")
    KILL_VOLUME = 0.01
    
    ENEMY_DEATH_PATHS = [
        Resources.get_path("sounds/enemy_death_1.ogg" if _is_web else "sounds/enemy_death_1.wav"),
        Resources.get_path("sounds/enemy_death_2.ogg" if _is_web else "sounds/enemy_death_2.wav")
    ]
    ENEMY_DEATH_VOLUME = 0.04
    
    SHOOT_PATH = Resources.get_path("sounds/shoot.ogg" if _is_web else "sounds/shoot.wav")
    SHOOT_VOLUME = 0.04
    
    RELOAD_PATH = Resources.get_path("sounds/reload.ogg" if _is_web else "sounds/reload.wav")
    RELOAD_VOLUME = 0.03
    
    POTION_PATH = Resources.get_path("sounds/potion.ogg" if _is_web else "sounds/potion.wav")
    POTION_VOLUME = 0.2


class UI:
    DEFAULT_FONT_NAME = "consolas"
    MAIN_FONT_PATH = Resources.get_path("fonts/NanumSquareR.ttf")
    
    FONT_SIZE_XXL = 72
    FONT_SIZE_XL  = 54
    FONT_SIZE_L   = 36
    FONT_SIZE_M   = 24
    FONT_SIZE_S   = 14


class Map:
    TILE       = 64 # 타일 당 크기
    MAX_STEPS  = 30 # 레이 탐색 제한
    
    ENEMIES_SPAWN_POS = [
        (6.5,   2.5),   # 좌상단 복도
        (13.5,  2.5),   # 우상단 복도
        (16.5,  2.5),   # 우상단 끝
        (9.5,   4.5),   # 중앙 상단
        (12.5,  5.5),   # 중앙 우측
        (16.5,  5.5),   # 우측 통로
        (2.5,   6.5),   # 좌측 통로
        (6.5,   6.5),   # 좌중단
        (14.5,  7.5),   # 우중단
        (6.5,   9.5),   # 중앙 좌측
        (9.5,   9.5),   # 중앙
        (16.5,  9.5),   # 우측 중단
        (11.5,  11.5),   # 중앙 하단
        (16.5,  12.5),   # 우하단
        (2.5,   13.5),   # 좌하단
        (13.5,  13.5),   # 우하단 복도
    ]


class Camera:
    FOV      = math.pi / 3
    HALF_FOV = FOV / 2

    NUM_RAYS     = Game.SCREEN_WIDTH // 2
    DELTA_ANGLE  = FOV / NUM_RAYS
    SCALE        = Game.SCREEN_WIDTH // NUM_RAYS
    PROJ_DIST    = NUM_RAYS / (2 * math.tan(HALF_FOV))
    
    SENSITIVITY_X = 0.0008    # 마우스 감도 (yaw)
    SENSITIVITY_Y = 0.3    # 마우스 감도 (pitch)
    PITCH_LIMIT = 600      # 최대 상하 이동 픽셀
    
    OFFSET_Y_SLIDING = -38.0    # 슬라이딩 중 카메라 높이 오프셋
    
  
class Player:
    MAX_HP = 100
    
    POTION_COUNT = 3
    POTION_HEAL_AMOUNT = 40
    
    MOVE_SPEED = 2.5
    
    # 점프 상수
    JUMP_VELOCITY  = 400.0    # 초기 상승 속도 (월드 유닛/초)
    GRAVITY        = 981.0    # 중력 가속도

    # 슬라이딩 상수
    SLIDE_DURATION  = 0.6     # 슬라이딩 지속 시간 (초)
    SLIDE_SPEED     = 3.4     # 슬라이딩 속도 배율
    
    HIT_TIME_FACTOR = 4.0   # 피격 시간: 0.25초
    KILL_TIME = 1.5         # 피격 시간: 0.25초


class Gun:
    MAX_AMMO = 50
    
    SHOOT_DAMAGE_MIN    = 5
    SHOOT_DAMAGE_MAX    = 10
    SHOOT_COOL          = 0.1
    SHOOT_RECOIL_AMOUNT = 4.5
    
    RELOAD_TIME = 1.28
    

class Enemy:
    SPRITE_PATH = Resources.get_path("images/enemy.png")
    SPRITE_DEAD_PATH = Resources.get_path("images/enemy_dead.png")
    
    STATE_IDLE   = 'idle'
    STATE_CHASE  = 'chase'
    STATE_ATTACK = 'attack'
    STATE_DEAD   = 'dead'

    SIGHT_DIST = 380
    
    MAX_HP = 30
    
    MOVE_SPEED = 1.4
    
    ATTACK_DIST       = 25
    ATTACK_DAMAGE_MIN = 10
    ATTACK_DAMAGE_MAX = 20
    ATTACK_COOL       = 1.0
    
    SCALE_FACTOR = 0.8


class Color:
    WHITE      = (255, 255, 255)
    GREEN      = (0, 200, 0)
    CEILING    = (50, 50, 50)
    FLOOR      = (30, 30, 30)
