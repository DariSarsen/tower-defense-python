import cocos.menu
import cocos.scene
import cocos.layer
import cocos.actions as ac
from cocos.director import director
from cocos.scenes.transitions import FadeBLTransition

import pyglet.app

from gamelayer import new_game


class MainMenu(cocos.menu.Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Tower Defense')

        self.font_title['font_name'] = 'Comic Sans MS'
        self.font_item['font_name'] = 'Comic Sans MS'
        self.font_item_selected['font_name'] = 'Comic Sans MS'

        self.menu_anchor_y = 'center'
        self.menu_anchor_x = 'center'

        items = list()

        items.append(cocos.menu.MenuItem('New Game', self.on_new_game))
        items.append(cocos.menu.MenuItem('Quit', pyglet.app.exit))

        self.create_menu(items, ac.ScaleTo(1.25, duration=0.25), ac.ScaleTo(1.0, duration=0.25))

    def on_new_game(self):
        director.push(FadeBLTransition(new_game(), duration=2))


def new_menu():
    scene = cocos.scene.Scene()
    color_layer = cocos.layer.ColorLayer(203, 129, 33, 255)
    scene.add(MainMenu(), z=1)
    scene.add(color_layer, z=0)
    return scene
