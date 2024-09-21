from .base_screen import BaseScreen

import mopidy.models

from ..graphic_utils import ListView
from ..input import InputManager
from .. import utils


class FolderScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.list_view = ListView((0, 0), self.size, self.base_size, self.fonts['base'])
        self.directory_list = []
        self.position_list = []
        self.current_directory = None
        self.browse_uri(None)

    def go_inside_directory(self, uri, position):
        self.directory_list.append(self.current_directory)
        self.position_list.append(position)
        self.current_directory = uri
        self.browse_uri(uri)

    def go_up_directory(self):
        if len(self.directory_list):
            directory = self.directory_list.pop()
            self.current_directory = directory
            self.browse_uri(directory)
            self.list_view.set_selected(self.position_list.pop())

    def should_update(self):
        return self.list_view.should_update()

    def find_update_rects(self, rects):
        return self.list_view.find_update_rects(rects)

    def update(self, screen, update_type, rects):
        update_all = (update_type == BaseScreen.update_all)
        self.list_view.render(screen, update_all, rects)
