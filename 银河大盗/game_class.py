import os, pygame
from pygame.locals import *
from func import *
from game_class import *
import random
#一些参数
ALIEN_ODDS     = 120   #敌人出现的频率，越大，敌人出现的越慢
ALIEN_CHECK    = 0     #检测游戏中有多少个敌人
DYNAMIC_SPAWN  = 4     #For Dynamic Spawning
BOMB_ODDS      = 200   #敌人发射子弹的概率，越大越不易发射子弹

# 定义游戏中需要的类
class Player(pygame.sprite.Sprite):
    speed = 5
    bounce = 24
    #发射子弹的点，设置一定的偏移量
    gun_offset = -11
    images = []
    score = 0
    weapon = 'Green Projectile'  #初始武器

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)  #直接导入pygame中的方法
        self.image = pygame.image.load(os.path.join('data', 'Player1.png')).convert_alpha()
        #分解图片
        self.images = [self.image, pygame.transform.flip(self.image, 1, 0)]
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        #将对象放在屏幕中间
        self.rect = self.image.get_rect(midbottom=self.area.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        #对象朝左，右为1
        self.facing = -1

    def move(self, direction):
        if direction: self.facing = direction
        #调用pygame中的move_ip方法
        self.rect.move_ip(direction * self.speed, 0)
        #保持角色在游戏屏幕中央
        self.rect = self.rect.clamp(self.area)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    #用于确定弹丸产生枪的原点
    def gunPosition(self):
        position = self.facing * self.gun_offset + self.rect.centerx
        return position, self.rect.top


# 第一个敌人:从左到右，在内部投下一颗炸弹，只能被玩家的绿色武器杀死
class Enemy1(pygame.sprite.Sprite):
    gun_offset = 11
    shootCounter = 0

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'Enemy1.png')).convert_alpha()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 1
        positionX = random.randint(0, 550)
        self.rect.topleft = positionX, 0

    def update(self):
        pos = self.rect.move(self.speed, 0)
        #左右移动
        if self.rect.left < self.area.left or self.rect.right > self.area.right:
            self.speed = -self.speed
            pos = self.rect.move(self.speed, 0)
        self.rect = pos
        self.shootCounter = self.shootCounter + 1

    def gunPosition(self):
        position = self.gun_offset + self.rect.centerx
        return position, self.rect.bottom


# 第二个敌人:上升和下降，如果两者相撞就会撞到玩家。只能被玩家的红色武器杀死
class Enemy2(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'Enemy2.png')).convert_alpha()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 2
        positionX = random.randint(0, 550)
        self.rect.topleft = positionX, 0
    #进行上下移动
    def update(self):
        pos = self.rect.move(0, self.speed)
        #进行上下移动
        if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
            self.speed = -self.speed
            pos = self.rect.move(0, self.speed)
        self.rect = pos


#第三个敌人:走斜线模式，总是会在屏幕的某一段上面，仍炸弹。只能被玩家的黄色武器杀死
class Enemy3(pygame.sprite.Sprite):
    shootCounter = 0
    gun_offset = 11

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'Enemy3.png')).convert_alpha()
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speedX = 2
        self.speedY = 2
        positionX = random.randint(0, 550)
        self.rect.topleft = positionX, 0

    def update(self):
        pos = self.rect.move(0, self.speedY)
        #走斜线
        if (self.rect.bottom > self.area.bottom / 3):
            pos = self.rect.move(self.speedX, self.speedY / 2)
        #防止黄色敌人越过屏幕的1/3与我方相撞
        if (self.rect.bottom > self.area.bottom - self.area.bottom / 3):
            self.speedY = -self.speedY
            pos = self.rect.move(0, self.speedY)
        #左右反弹
        if self.rect.left < self.area.left or self.rect.right > self.area.right:
            self.speedX = -self.speedX
            pos = self.rect.move(self.speedX, 0)
        #上下反弹
        if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
            self.speedY = -self.speedY
            pos = self.rect.move(0, self.speedY * 2)
        self.rect = pos
        #自身定时器
        self.shootCounter = self.shootCounter + 1

    def gunPosition(self):
        position = self.gun_offset + self.rect.centerx
        return position, self.rect.bottom

#子弹类
class Projectile(pygame.sprite.Sprite):
    speed = -11

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class GreenProjectile(Projectile):  # Inherit from Projectile
    def __init__(self, position):
        Projectile.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'projectile1.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom=position)


class RedProjectile(Projectile):
    def __init__(self, position):
        Projectile.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'projectile2.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom=position)


class YellowProjectile(Projectile):
    def __init__(self, position):
        Projectile.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'projectile3.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom=position)


class EnemyProjectile(Projectile):
    def __init__(self, position):
        Projectile.__init__(self)
        self.speed = 1
        self.image = pygame.image.load(os.path.join('data', 'projectile4.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom=position)

#爆炸
class Explode(pygame.sprite.Sprite):
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('explosion1.gif')
        self.rect = self.image.get_rect(center=actor.rect.center)

    def update(self):
        self.kill()
#生成一个随机敌人
def spawnRandomEnemy(enemiesType1, enemiesType2, enemiesType3, allsprites):
    global ALIEN_CHECK
    #随机生成1到3类型
    spawnNumber = random.randint(1, 3)

    if spawnNumber == 1:
        newenemy = Enemy1()
        enemiesType1.add(newenemy)
        allsprites.add(newenemy)
        ALIEN_CHECK = ALIEN_CHECK + 1
    elif spawnNumber == 2:
        newenemy = Enemy2()
        enemiesType2.add(newenemy)
        allsprites.add(newenemy)
        ALIEN_CHECK = ALIEN_CHECK + 1
    elif spawnNumber == 3:
        newenemy = Enemy3()
        enemiesType3.add(newenemy)
        allsprites.add(newenemy)
        ALIEN_CHECK = ALIEN_CHECK + 1
        # print('Added')

#生成怪物发射的随机炸弹
def spawnBomb(allsprites, enemy, projectilesEnemy):
    global BOMB_ODDS
    #比一个随机数大，将发射子弹，并将shootCounter清0
    if (enemy.shootCounter >= BOMB_ODDS + random.randint(1, 200)):
        # if (enemy.shootCounter >= BOMB_ODDS + random.randint(1,30)):
        # print('Shooting at: ', enemy.shootCounter)
        newShtE = EnemyProjectile(enemy.gunPosition())
        projectilesEnemy.add(newShtE)
        allsprites.add(newShtE)
        enemy.shootCounter = 0



