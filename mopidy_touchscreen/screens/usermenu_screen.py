import os
import socket

from .base_screen import BaseScreen

from ..graphic_utils import ListView


class UserMenuScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts, core, config):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.ip = None
        self.core = core
        self.list = ListView((0, 0), size,
                             base_size, fonts['base'])

        conffile = os.path.join(config['core']['config_dir'], 'usermenu.conf')

        self.list_items = []
        self.commands = []

        try:
            with open(conffile, 'r') as f:
                for l in f:
                    sep = l.find('\t');
                    self.list_items.append(l[0:sep])
                    self.commands.append(l[sep+1:])
        except:
            self.list_items = [ 'Error Loading' ]
            self.commands = [ '' ]

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
            os.system(self.commands[clicked])
