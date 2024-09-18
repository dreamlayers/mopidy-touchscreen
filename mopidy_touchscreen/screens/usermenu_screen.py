import os
import socket

from .base_screen import BaseScreen

from ..graphic_utils import ListView


class UserMenuScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts, core):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.ip = None
        self.core = core
        self.list = ListView((0, 0), size,
                             base_size, fonts['base'])

        self.list_items = ["Test Random", "Test Repeat"]

        self.list.set_list(self.list_items)

    def should_update(self):
        return self.list.should_update()

    def find_update_rects(self, rects):
        return self.list_view.find_update_rects(rects)


    def update(self, screen, update_type, rects):
        update_all = (update_type == BaseScreen.update_all)
        self.list.render(screen, update_all, rects)

    def touch_event(self, event):
        clicked = self.list.touch_event(event)
        if clicked is not None:
            if clicked == 0:
                random = not self.core.tracklist.get_random().get()
                self.core.tracklist.set_random(random)
            elif clicked == 1:
                repeat = not self.core.tracklist.get_repeat().get()
                self.core.tracklist.set_repeat(repeat)
