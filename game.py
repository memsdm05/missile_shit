import pyglet
from pyglet.gl import *
from pyglet.window import key
import sys
import math as m
import random as r



# Bulletin
# todo work on background tessilation + open-world
# todo move player and enemy code to seperate classes
# todo missile module

class Background:
    def __init__(self, IMAGE):
        self.back_img = pyglet.image.load(IMAGE)
        # self.back = pyglet.sprite.Sprite(self.back_img)
        self.batch_draw()

    # temp background drawer to allow time for real shit
    def batch_draw(self):
        self.back = pyglet.graphics.Batch()

        self.b_sprites = []
        # create a grid of batched sprites that act as backgrounds
        for X in range(20):
            for Y in range(20):
                x, y = X * self.back_img.width, Y * self.back_img.height
                offset_bunch = [pyglet.sprite.Sprite(self.back_img, x, y, subpixel=True, batch=self.back), x, y]
                self.b_sprites.append(offset_bunch)

    def local_draw(self, x, y, loading_radius=3):
        self.back = pyglet.graphics.Batch()

        self.b_sprites = []
        chunk_x, chunk_y = self.get_chunk(-x, -y)
        for X in range(chunk_x-loading_radius, chunk_x+loading_radius+1):
            for Y in range(chunk_y-loading_radius, chunk_y+loading_radius+1):
                x, y = X * self.back_img.width, Y * self.back_img.height
                offset_bunch = [pyglet.sprite.Sprite(self.back_img, x, y, subpixel=True, batch=self.back), x, y]
                self.b_sprites.append(offset_bunch)

    # update ALL the backgrounds (aka the grid)
    def update_all(self, x, y, w, h):
        for s in self.b_sprites:
            mx = x+s[1]+w/2
            my = y+s[2]+h/2

            s[0].update(mx, my)  # offset by half a screen so 0, 0 is bottom left

    def get_chunk(self, x, y):
        return int(x//self.back_img.width), int(y//self.back_img.height)


class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_variable()
        self.setup_sprites()

    def setup_sprites(self):
        # Load player skin
        self.ball_image = pyglet.image.load('images/player.png')
        self.ball_image.anchor_y = self.ball_image.height // 2
        self.ball_image.anchor_x = self.ball_image.width // 2
        self.player = pyglet.sprite.Sprite(self.ball_image, x=self.x, y=self.y, subpixel=True)

        # load background stuff
        self.stuff = Background('images/back.jpg')

        # Load enemy skin
        self.enemy_image = pyglet.image.load('images/enemy.png')
        self.enemy_image.anchor_y = self.enemy_image.height // 2
        self.enemy_image.anchor_x = self.enemy_image.width // 2
        self.enemy = pyglet.sprite.Sprite(self.enemy_image, x=self.x, y=self.y)

    # setup varibles
    def setup_variable(self):

        # location variables
        self.xR = 0
        self.yR = 0
        self.x = self.xR
        self.y = self.yR
        self.mouseX = 0
        self.mouseY = 0
        self.flipX = 0
        self.turn = 0

        # physics variables
        self.thrust = 1.0 #0.3
        self.thrustX = 0
        self.thrustY = 0
        self.diffX = 0
        self.diffY = 0

        # movement booleans
        self.press = False
        self.reverse = False
        self.brakes = False

    # Get angle of ship to mouse
    def angle(self):
        try:
            slope = (self.mouseY - (self.height/2)) / (self.mouseX - (self.width/2))
            self.turn = (360 - m.degrees(m.atan(slope))) - 360
            self.flipX = -1.0 if self.mouseX < self.width / 2 else 1.0
        except:
            self.flipX = -1.0 if self.mouseY > self.height / 2 else 1.0
            self.turn = 90
        # print(slope)

    # todo flying sucks a** plz fix make better please
    # done
    def physics_engine(self):
        self.x += self.thrustX
        self.y += self.thrustY

        self.speed = m.sqrt(self.thrustX ** 2 + self.thrustY ** 2)
        self.thrust = m.sqrt(((self.height/2)-self.mouseY)**2 + ((self.width/2)-self.mouseX)**2) / 400
        self.thrust = 0.8 if self.thrust > 0.8 else self.thrust

        if self.press:
            self.diffX = self.thrust * (m.cos(m.radians(abs(self.turn))))
            self.diffY = self.thrust * (m.sin(m.radians(abs(self.turn))))

            self.diffX = self.diffX if self.mouseX < self.width/2 else -self.diffX
            self.diffY = self.diffY if self.mouseY < self.height/2 else -self.diffY

            if self.reverse:
                self.thrustX -= self.diffX
                self.thrustY -= self.diffY
            else:
                self.thrustX += self.diffX
                self.thrustY += self.diffY
        if self.brakes:
            self.thrustX *= 0.95
            self.thrustY *= 0.95

    def effects(self):
        self.shake  = r.uniform(-1, 1) * self.speed / 30 if self.press else 0
        self.shake2 = r.uniform(-1, 1) * self.speed / 30 if self.press else 0

    def on_draw(self):
        self.clear()
        self.physics_engine()

        # self.back.anchor_x = self.back.width // 2
        # self.back.anchor_y = self.back.height // 2

        self.stuff.local_draw(self.x, self.y, 3)
        self.stuff.update_all(self.x, self.y, self.width, self.height)
        self.stuff.back.draw()

        label = pyglet.text.Label(f'{(self.stuff.get_chunk(self.x, self.y))}{-int(self.x)} {-int(self.y)} {int(self.turn)} {int(self.speed)} {int(self.thrust*100)/100}',
                                  font_size=12,
                                  x=self.width-10, y=self.height-20,
                                  anchor_x='right', anchor_y='center')
        label.draw()



        glLineWidth(10)
        if self.thrust != 0.8:
            glColor3f(self.thrust, self.thrust, self.thrust)
        else:
            glColor3f(1., 0., 0.)

        self.effects()
        if self.press:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                                 ('v2f', ((self.width/2)+self.shake, (self.height/2)+self.shake2,
                                 (self.mouseX+self.width/2)*0.5, (self.mouseY+self.height/2)*0.5 )))
        self.angle()
        self.player.update((self.width/2)+self.shake, (self.height/2)+self.shake2, scale=0.5, rotation=self.turn, scale_x=self.flipX)
        self.player.draw()

        # if self.x > self.width + 5: self.x = 0
        # if self.x < -5: self.x = self.width
        # if self.y > self.height + 5: self.y = 0
        # if self.y < -5: self.y = self.height

        # self.enemy.update(100, 100, scale_x=(r.random()*0.04)+1.3, scale_y=(r.random()*0.04)+1.3)
        # self.enemy.draw()

        # print(self.press)


    def on_mouse_press(self, x, y, button, modifiers):
        self.mouseX = x
        self.mouseY = y


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouseX = x
        self.mouseY = y


    def on_mouse_motion(self, x, y, dx, dy):
        self.mouseX = x
        self.mouseY = y

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            sys.exit()
        elif symbol == key.T:
            self.brakes = True
            #self.thrustX = 0
            #self.thrustY = 0

        elif symbol == key.R:
            self.x = self.xR
            self.y = self.yR
            self.thrustX = 0
            self.thrustY = 0

        elif symbol == key.W or symbol == key.SPACE:
            self.press = True
        elif symbol == key.S:
            self.press = True
            self.reverse = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W or symbol == key.SPACE:
            self.press = False
        elif symbol == key.S:
            self.press = False
            self.reverse = False
        elif symbol == key.T:
            self.brakes = False

    def on_close(self):
        sys.exit()



def main():

    window = Game(1080, 720, "Missile Command", resizable=True)
    window.set_minimum_size(1080, 720)
    window.set_icon(pyglet.image.load('images/thumb.png'))

    FPS  = pyglet.window.FPSDisplay(window)

    cursor = window.get_system_mouse_cursor(window.CURSOR_CROSSHAIR)
    window.set_mouse_cursor(cursor)
    window.switch_to()
    window.on_draw()

    # pyglet.app.run()

    # Game loop (for some reason this works better than the standard way)
    while True:
        pyglet.clock.tick()

        window.switch_to()
        window.dispatch_events()
        window.dispatch_event('on_draw')
        FPS.draw()

        window.flip()

if __name__ == '__main__':
    main()
