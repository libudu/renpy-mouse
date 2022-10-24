define config.mouse = {
    'default': [
        ('mouse.png', 0, 0)
    ],
    'mousedown': [
        ('mousedown.png', 0, 0)
    ],
    'mousehover': [
        ('mousehover.png', 0, 0)
    ],
}

# renpy暂未提供鼠标按下时的定制接口
# 通过替换Interface中的原有方法来实现定制鼠标按下时的光标变化
init python:
    import pygame
    Interface = renpy.display.core.Interface

    def _mock_get_mouse_name(self, cache_only=False, interaction=True):
        global _old_get_mouse_name        
        if renpy.config.mouse.get("mousedown") != None and pygame.mouse.get_pressed()[0]:
            return "mousedown"
        return Interface._old_get_mouse_name(self, cache_only, interaction)
    
    # 先判断是否已存在，避免交互式编辑启动时会重载init python代码，导致递归
    if not hasattr(Interface, "_old_get_mouse_name"):
        Interface._old_get_mouse_name = Interface.get_mouse_name
        Interface.get_mouse_name = _mock_get_mouse_name    


# 使用transform做动态可视组件
transform MouseSnowTransform(last_time, rotate):
    im.FactorScale("mouse.png", 0.2)
    parallel:
        linear last_time alpha 0.0
    parallel:
        linear last_time rotate rotate

init python:
    # 下雪的鼠标
    import random
    class MouseSnow():
        def __init__(self):
            # 持续时间
            self.last_time = 1
            # 下落的可视组件
            self.snow_image_list = [
                MouseSnowTransform(self.last_time, 360),
                MouseSnowTransform(self.last_time, 180),
                MouseSnowTransform(self.last_time, -360),
                MouseSnowTransform(self.last_time, -180),
            ]
            # 下落区域的宽度
            self.snow_width = 50
            # 每隔多少秒生成一个
            self.break_time = 0.1
            # 下落速度
            self.speed_y = 1.5
            # 控制是否继续生成
            self.open = False

            # 同屏最大数量，等于持续时间/间隔生成时间
            self.max_count = self.last_time / self.break_time
            self.sprite_list = []
            self.sprite_manager = SpriteManager(update=self.sprite_update)
        
        # 粒子不断下落
        def sprite_update(self, st):
            for i in self.sprite_list:
                i.y += self.speed_y
            return 0.01
        
        # 生成一个粒子
        def add_sprite(self):
            if self.open:
                snow_image = random.choice(self.snow_image_list)
                sprite = self.sprite_manager.create(snow_image)
                mouse_pos = renpy.get_mouse_pos()
                sprite.x = mouse_pos[0]
                sprite.y = mouse_pos[1]
                sprite.x += random.random() * self.snow_width
                self.sprite_list.append(sprite)
                # 超过最大存在数则移除第一个
                if len(self.sprite_list) > self.max_count:
                    self.sprite_list.pop(0).destroy()
    
    mouse_snow = MouseSnow()
    # 光标雪花效果的置顶图层
    config.top_layers.append("mouse")

# 光标雪花效果的界面
screen MouseSnowScreen():
    layer "mouse"
    add mouse_snow.sprite_manager
    timer mouse_snow.break_time action mouse_snow.add_sprite repeat True

# 进入主菜单之前，开始显示鼠标界面
label before_main_menu:
    show screen MouseSnowScreen