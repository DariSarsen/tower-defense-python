import random

from cocos.director import director
from cocos.scenes.transitions import SplitColsTransition, FadeTransition
import cocos.layer
import cocos.scene
import cocos.text
import cocos.actions as ac
import cocos.collision_model as cm

import actors
import mainmenu
from scenario import get_scenario


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, hud, scenario):
        super(GameLayer, self).__init__()
        self.hud = hud
        self.scenario = scenario
        self.score = self._score = 0
        self.points = self._points = 60
        self.turrets = []

        w, h = director.get_window_size()
        cell_size = 32
        self.coll_man = cm.CollisionManagerGrid(0, w, 0, h, cell_size, cell_size)
        self.coll_man_slots = cm.CollisionManagerGrid(0, w, 0, h, cell_size, cell_size)
        for slot in scenario.turret_slots:
            self.coll_man_slots.add(actors.TurretSlot(slot, cell_size))

        self.bunker = actors.Bunker(*scenario.bunker_position)
        self.add(self.bunker)
        self.schedule(self.game_loop)

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, val):
        self._points = val
        self.hud.update_points(val)

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, val):
        self._score = val
        self.hud.update_score(val)

    def game_loop(self, _):
        self.coll_man.clear()
        for obj in self.get_children():
            if isinstance(obj, actors.Enemy):
                self.coll_man.add(obj)

        for turret in self.turrets:
            obj = next(self.coll_man.iter_colliding(turret), None)
            turret.collide(obj)
        for obj in self.coll_man.iter_colliding(self.bunker):
            self.bunker.collide(obj)

        if random.random() < 0.005:
            self.create_enemy()

    def create_enemy(self):
        enemy_start = self.scenario.enemy_start
        x = enemy_start[0] + random.uniform(-10, 10)
        y = enemy_start[1] + random.uniform(-10, 10)
        self.add(actors.Enemy(x, y, self.scenario.actions))

    def on_mouse_press(self, x, y, buttons, mod):
        slots = self.coll_man_slots.objs_touching_point(x, y)
        if len(slots) and self.points >= 20:
            self.points -= 20
            slot = next(iter(slots))
            turret = actors.Turret(*slot.cshape.center)
            self.turrets.append(turret)
            self.add(turret)

    def remove(self, obj):
        if obj is self.bunker:
            director.replace(SplitColsTransition(game_over()))
        elif isinstance(obj, actors.Enemy) and obj.destroyed:
            self.score += obj.score
            self.points += 5
        super(GameLayer, self).remove(obj)


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = director.get_window_size()
        self.score_text = self._create_text(60, h-40)
        self.score_points = self._create_text(w-60, h-40)

    def _create_text(self, x, y):
        text = cocos.text.Label(font_size=18, font_name='Oswald',
                                anchor_x='center', anchor_y='center')
        text.position = (x, y)
        self.add(text)
        return text

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_points(self, points):
        self.score_points.element.text = 'Points: %s' % points


def new_game():
    scenario = get_scenario()
    background = scenario.get_background()
    hud = HUD()
    game_layer = GameLayer(hud, scenario)
    return cocos.scene.Scene(background, game_layer, hud)


def game_over():
    w, h = director.get_window_size()
    layer = cocos.layer.Layer()
    text = cocos.text.Label('Game Over', position=(w * 0.5, h * 0.5),
                            font_name='Oswald', font_size=72,
                            anchor_x='center', anchor_y='center')
    layer.add(text)
    scene = cocos.scene.Scene(layer)
    new_scene = FadeTransition(mainmenu.new_menu())
    func = lambda: director.replace(new_scene)
    scene.do(ac.Delay(3) + ac.CallFunc(func))
    return scene
