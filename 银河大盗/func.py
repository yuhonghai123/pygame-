import pygame,os
#简化一些函数，使得调用方便
#游戏目录
main_dir = os.path.split(os.path.abspath(__file__))[0]
def load_image(file):
    "加载一个图片"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

#如果pygame.mixer不能运行，该模块将运行
class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
    except pygame.error:
        print ('不能加载, %s' % file)
    return sound
