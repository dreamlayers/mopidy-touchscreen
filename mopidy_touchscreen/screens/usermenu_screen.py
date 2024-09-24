import os
import socket

from .folder_screen import FolderScreen
from ..input import InputManager
from ..graphic_utils import ListView

class UserMenuScreen(FolderScreen):
    @staticmethod
    def load_config(filename):
        last = [ ( [], [] ) ]
        with open(filename, 'r') as f:
            for l in f:
                l = l.rstrip('\r\n')
                llen = len(l)
                l = l.lstrip('\t')
                tlev = llen - len(l)
                clev = len(last) - 1
                if tlev == 0 and l == '':
                    # Blank line ends one level, going back to parent level
                    if len(last) > 1:
                        last.pop()
                elif tlev <= clev:
                    # Adding item to current menu level
                    sep = l.find('\t');
                    if sep >= 0:
                        last[-1][0].append(l[0:sep])
                        last[-1][1].append(l[sep+1:])
                    else:
                        last[-1][0].append(l)
                        last[-1][1].append(None)
                elif tlev == clev + 1:
                    # Start new inner level
                    last[-1][0].append(l)
                    newmenu = (['../'], [ ])
                    last[-1][1].append(newmenu)
                    last.append(newmenu)

        return last[0]

    def reload(self, first = False):
        try:
            self.menu = UserMenuScreen.load_config(self.conffile)
        except:
            self.menu = ( [ 'Error Loading' ], [ None ] )

        self.menu[0].append('Reload menu')
        self.menu[1].append(self.reload)

        if not first:
            self.browse_uri(None)

    def __init__(self, size, base_size, manager, fonts, core, config):
        self.ip = None
        self.core = core
        self.list = ListView((0, 0), size,
                             base_size, fonts['base'])

        self.conffile = os.path.join(config['core']['config_dir'],
                                     'usermenu.conf')
        self.reload(True)

        FolderScreen.__init__(self, size, base_size, manager, fonts)

    def browse_uri(self, uri):
        if uri is None:
            uri = self.menu

        self.list_view.set_list(uri[0])
        self.actions = uri[1]

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event,
            (InputManager.enter, InputManager.enqueue, InputManager.back))
        if clicked is not None:
            if self.current_directory is not None and \
               ((touch_event.type == InputManager.key and
                touch_event.direction == InputManager.back) or clicked == 0):
                self.go_up_directory()
            elif touch_event.type != InputManager.key or \
                 touch_event.direction == InputManager.enter:
                if self.current_directory is not None:
                    action = self.actions[clicked-1]
                else:
                    action = self.actions[clicked]

                if isinstance(action, str):
                    os.system(action)
                elif isinstance(action, tuple):
                    self.go_inside_directory(action, clicked)
                elif callable(action):
                    action()
