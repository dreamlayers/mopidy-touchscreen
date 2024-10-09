import os
import socket

from .folder_screen import FolderScreen
from ..input import InputManager
from ..graphic_utils import ListView

class UserMenuScreen(FolderScreen):
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    @staticmethod
    def import_from_path(module_name, file_path):
        import importlib.util
        import sys
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def load_config(confdir):
        last = [ ( [], [] ) ]
        helper = None
        with open(os.path.join(confdir, 'usermenu.conf'), 'r') as f:
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
                        action = l[sep+1:]
                        if action.startswith('//'):
                            if helper is None:
                                try:
                                    helper = UserMenuScreen.import_from_path(
                                        'usermenu',
                                        os.path.join(confdir, 'usermenu.py')
                                    ).UserMenuHelper()
                                except Exception as e:
                                    print("Error loading UserMenuHelper:")
                                    print(e)
                                    helper = False
                            if helper is not None and helper != False:
                                try:
                                    action = getattr(helper, action[2:])
                                except Exception as e:
                                    print('Error finding helper function ' +
                                          action[2:] + ':')
                                    print(e)
                                    action = None
                        last[-1][1].append(action)
                    else:
                        last[-1][0].append(l)
                        last[-1][1].append(None)
                elif tlev == clev + 1:
                    last[-1][0].append(l)
                    newmenu = (['../'], [ ])
                    last[-1][1].append(newmenu)
                    last.append(newmenu)

        return last[0]

    def reload(self):
        try:
            self.menu = UserMenuScreen.load_config(self.confdir)
        except Exception as e:
            print("Error loading user menu:")
            print(e)
            self.menu = ( [ 'Error Loading' ], [ None ] )

        self.menu[0].append('Reload menu')
        self.menu[1].append(self.reload)

        return True

    def __init__(self, size, base_size, manager, fonts, core, config):
        self.ip = None
        self.core = core
        self.list = ListView((0, 0), size,
                             base_size, fonts['base'])

        self.confdir = config['core']['config_dir']
        self.reload()

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
                    res = action()
                    if isinstance(res, tuple):
                        self.go_inside_directory(res, clicked)
                    elif res:
                        self.browse_root()
