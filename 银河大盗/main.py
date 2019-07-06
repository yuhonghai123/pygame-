"""
银河大盗


作者：电计1704 于洪海
学号：201763009

一个简单的太空主题射击游戏的介绍：

规则:
1. 有三种类型的攻击对应于不同的颜色:红色、绿色和黄色
2. 也有三种不同类型的敌人与这些颜色相对应
3.每个敌人的弱点都是由敌人的颜色决定的
4. 利用敌人的弱点将打败他们，这是胜利的关键
5. 每艘船只能被击中一次，包括你的船。保持敏锐，避免你的敌人的演习和他们的炮弹!
6. 1分钟后，你将在战斗中幸存下来，你将被宣布为胜利者
控制:
1 - 3键:分别切换到绿色，红色和黄色武器
空格键:用装备好的武器射击
左:移动离开
右:向右移动
ESC:退出屏幕
"""
import os, pygame #
from pygame.locals import *
from func import *
from game_class import *
import random
from goto import with_goto #使用goto语句帮助跳转
if not pygame.mixer: print ('Warning, sound disabled')
if not pygame.font: print ('Warning, fonts disabled')

#一些参数
#ALIEN_RELOAD   = 12    #敌人出现的帧数
ALIEN_ODDS     = 120   #敌人出现的频率，越大，敌人出现的越慢
ALIEN_CHECK    = 0     #检测游戏中有多少个敌人
DYNAMIC_SPAWN  = 4     #For Dynamic Spawning
BOMB_ODDS      = 200   #敌人发射子弹的概率，越大越不易发射子弹
#将在程序中调用goto语句
#flag与goto相配合使用
flag = 0
@with_goto
def main():
    #设置一些参数为全局变量
    global ALIEN_ODDS
    global ALIEN_CHECK
    global DYNAMIC_SPAWN
    #生成敌人时需要
    counter = 0
    counter2 = 0
    counter3 = 0
    running = True
    titleScreen = True
    gameOver = True
    win      =False
    #For the moving background
    y = 0
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = -480
    
    #对所有进行初始化
    pygame.init()
    pygame.display.set_caption('Space Pirate')

    #创建背景
    background = pygame.image.load(os.path.join('data', 'background.png'))
    background_size = background.get_size()
    background_rect = background.get_rect()
    screen = pygame.display.set_mode(background_size)
    w,h = background_size
    x1 = 0
    y1 = -h

    #显示背景
    screen.blit(background, (0, 0))
    pygame.display.flip()
    label.end3#与goto语句有关
    #Prepare Game Objects
    clock = pygame.time.Clock()

    #如果熬过60秒，则游戏结束
    pygame.time.set_timer(pygame.USEREVENT, 60000)
    boom_sound = load_sound('boom.wav')
    shoot_sound = load_sound('car_door.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'bg_music.wav')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)
    player1 = Player()
    weaponColor = pygame.image.load(os.path.join('data', 'weapon1.png')).convert_alpha()
    enemy1 = Enemy1()
    enemy2 = Enemy2()
    enemy3 = Enemy3()

    #建立游戏对象的编组
    playerBucket = pygame.sprite.Group(player1)
    enemiesType1 = pygame.sprite.Group(enemy1)
    enemiesType2 = pygame.sprite.Group(enemy2)
    enemiesType3 = pygame.sprite.Group(enemy3)
    projectilesGreen = pygame.sprite.Group() #Initially empty (for collisions)
    projectilesRed = pygame.sprite.Group()
    projectilesYellow = pygame.sprite.Group()
    projectilesEnemy = pygame.sprite.Group()
    allsprites = pygame.sprite.RenderPlain((player1, enemy1, enemy2)) #Add everyone to another group (in order to update all simultaneously)

    #游戏起始画面

    if pygame.font:
            font = pygame.font.Font('freesansbold.ttf', 36)
            start_text = font.render('Press ENTER to Start', 1, (255, 255, 255))
            start_textPosition = start_text.get_rect()
            start_textPosition.midtop = (screen.get_width()/2, screen.get_height() * 3/4)
    #起始画面的循环
    while titleScreen == True:
        #处理输入信息
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                titleScreen = False
                #直接退出游戏，所以running = False
                running = False
        #按enter键进入游戏
        keystate = pygame.key.get_pressed()

        if keystate[K_RETURN]:
            titleScreen = False

        #显示屏幕起始的图像
        logo = pygame.image.load(os.path.join('data', 'logo.png')).convert_alpha()
        screen.blit(logo, (w/6, h/8))
        screen.blit(start_text, start_textPosition)
        
        pygame.display.flip()

    #进入游戏主循环
    while running:

    # 将游戏的帧数设置为60
        clock.tick(60)

    #处理输入
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == pygame.USEREVENT:
                running = False
                win     = True

        keystate = pygame.key.get_pressed()
        #用bool值来描述方向的左右
        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        #调用方向函数，改变飞船方向
        player1.move(direction)
        #改变武器的颜色
        if keystate[K_1] or keystate[K_KP1]:
            player1.weapon = 'Green Projectile'
            weaponColor = pygame.image.load(os.path.join('data', 'weapon1.png')).convert_alpha()
        if keystate[K_2] or keystate[K_KP2]:
            player1.weapon = 'Red Projectile'
            weaponColor = pygame.image.load(os.path.join('data', 'weapon2.png')).convert_alpha()
        if keystate[K_3] or keystate[K_KP3]:
            player1.weapon = 'Yellow Projectile'
            weaponColor = pygame.image.load(os.path.join('data', 'weapon3.png')).convert_alpha()
        #在装子弹的时候不能开枪
        firing = keystate[K_SPACE]
        if not player1.reloading and firing:
            if player1.weapon == 'Green Projectile':
                #将子弹切换为绿色
                greenProjectile = GreenProjectile(player1.gunPosition())
                projectilesGreen.add(greenProjectile)
                allsprites.add(greenProjectile)
            elif player1.weapon == 'Red Projectile':
                redProjectile = RedProjectile(player1.gunPosition())
                projectilesRed.add(redProjectile)
                allsprites.add(redProjectile)
            elif player1.weapon == 'Yellow Projectile':
                yellowProjectile = YellowProjectile(player1.gunPosition())
                projectilesYellow.add(yellowProjectile)
                allsprites.add(yellowProjectile)
            shoot_sound.play()
    # 置reloading参数为0
        player1.reloading = firing

        allsprites.update()

        #检测碰撞
        for enemy in pygame.sprite.groupcollide(projectilesGreen, enemiesType1, 1, 1):
            explosion = Explode(enemy)
            # 爆炸动画将在下一帧进行显示
            allsprites.add(explosion)
            boom_sound.play()
            enemy.kill()
            ALIEN_CHECK = ALIEN_CHECK - 1
            player1.score += 1


            
        for enemy in pygame.sprite.groupcollide(projectilesRed, enemiesType2, 1, 1):
            explosion = Explode(enemy)
            allsprites.add(explosion)
            boom_sound.play()
            enemy.kill()
            player1.score += 1
            ALIEN_CHECK = ALIEN_CHECK - 1
                        
        for enemy in pygame.sprite.groupcollide(projectilesYellow, enemiesType3, 1, 1):
            explosion = Explode(enemy)
            allsprites.add(explosion)
            boom_sound.play()
            enemy.kill()
            player1.score += 1
            ALIEN_CHECK = ALIEN_CHECK - 1
        #敌人与玩家碰撞
        for enemy in pygame.sprite.groupcollide(playerBucket, enemiesType2, 1, 1):
            explosion = Explode(player1)
            allsprites.add(explosion)
            boom_sound.play()
            player1.kill()
            running = False
        #敌人的子弹与玩家碰撞
        for enemy in pygame.sprite.groupcollide(playerBucket, projectilesEnemy, 1, 1):
            explosion = Explode(player1)
            allsprites.add(explosion)
            boom_sound.play()
            player1.kill()
            running = False


        #生成敌人
        counter = counter + 1
        #print(counter)
        #只有当counter中的数字足够大时，即大于ALIEN_ODDS时，才生成敌人
        if counter > ALIEN_ODDS :
            #print('ALIEN_CHECK BEFORE: ',ALIEN_CHECK)
            #敌人的数量小于4，即敌人太少了，要生成2，到3个敌人
            if ALIEN_CHECK < DYNAMIC_SPAWN:
                #生成2到3个随机敌人
                for i in range (random.randint(2,3)):
                    #生成随机敌人
                    spawnRandomEnemy(enemiesType1, enemiesType2, enemiesType3, allsprites)
                    #生成敌人后将计数器清0
                    counter = 0
                #改变生成敌人概率
                if ALIEN_ODDS <= 120:
                    ALIEN_ODDS = 300
                    #print('Alien_odds at: ', ALIEN_ODDS)
                else:
                    ALIEN_ODDS = ALIEN_ODDS - random.randint(0, 30)
                    #print('Alien_odds at: ', ALIEN_ODDS)
            #如果敌人的数量已经很多，大于ALIEN_CHECK
            else:
                    #只生成一个敌人
                    spawnRandomEnemy(enemiesType1, enemiesType2, enemiesType3, allsprites)
                    counter = 0
                    #敌人很多，要减少生成敌人的速度
                    ALIEN_ODDS = ALIEN_ODDS + random.randint(0, 50)
                    #print('Alien_odds at: ', ALIEN_ODDS)
                    #print ('counter after: ' , counter)
                    #print('ALIEN_CHECK AFTER: ',ALIEN_CHECK)
        #生成敌人发射的炸弹
        for enemy in pygame.sprite.Group(enemiesType1):
            spawnBomb(allsprites, enemy, projectilesEnemy)

        for enemy in pygame.sprite.Group(enemiesType3):
            spawnBomb(allsprites, enemy, projectilesEnemy)


        #设置背景的变化
        y1 += 10
        y += 10
        screen.blit(background,(0, y))
        screen.blit(background,(x1, y1))
        if y > h:
            y = -h
        if y1 > h:
            y1 = -h
        allsprites.draw(screen)
    # 添加分数标签
        if pygame.font:
            font = pygame.font.Font('freesansbold.ttf', 36)
            text = font.render('Score: ' + str(player1.score), 1, (255, 255, 255)) # Score count
            #显示分数，第2个参数为显示的位置
            screen.blit(text, (50, 10))
        screen.blit(weaponColor, (10, 8)) #Weapon Type selected
        pygame.display.flip()

    #设置游戏结束
    if win == False:
        text1 = font.render('GAME OVER!', 1, (255, 255, 255))
    else:
        text1 = font.render('YOU WIN!!!', 1,(255, 0, 0) )
    textPosition1 = text1.get_rect()
    textPosition1.midtop = (screen.get_width()/2, screen.get_height()/2-50)
    text2 = font.render('Press ENTER To Continue!', 1, (255, 255, 255))
    textPosition2 = text2.get_rect()
    textPosition2.midtop = (screen.get_width() / 2, screen.get_height() / 2+50)
    #flag一直为0，除了goto将不会进入
    if flag ==1:
        label.end2
        goto.end3

    while gameOver:
        clock.tick(60)
        if flag == 1:
            label.end1
            goto .end2
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                gameOver = False
            elif event.type == KEYDOWN and event.key == K_RETURN:
                running=1
                goto .end1
        keystate = pygame.key.get_pressed()

        screen.blit(background, (0, 0))
        screen.blit(text1, textPosition1)
        screen.blit(text2, textPosition2)
        pygame.display.flip()
        
    pygame.quit()

if __name__ == '__main__': main()
