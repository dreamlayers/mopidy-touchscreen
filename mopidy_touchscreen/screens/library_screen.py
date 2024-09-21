from .folder_screen import FolderScreen

import mopidy.models

from ..graphic_utils import ListView
from ..input import InputManager
from .. import utils


class LibraryScreen(FolderScreen):
    def __init__(self, size, base_size, manager, fonts):
        self.library = None
        self.library_strings = None
        FolderScreen.__init__(self, size, base_size, manager, fonts)

    def browse_uri(self, uri):
        self.library_strings = []
        if uri is not None:
            self.library_strings.append("../")
        self.library = self.manager.core.library.browse(uri).get()
        for lib in self.library:
            self.library_strings.append(lib.name)
        self.list_view.set_list(self.library_strings)

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event,
            (InputManager.enter, InputManager.enqueue, InputManager.back))
        if clicked is not None:
            if self.current_directory is not None:
                if (touch_event.type == InputManager.key and
                    touch_event.direction == InputManager.back) or clicked == 0:
                    self.go_up_directory()
                else:
                    enqueue = touch_event.type == InputManager.key and \
                              touch_event.direction == InputManager.enqueue
                    if self.library[clicked - 1].type\
                            == mopidy.models.Ref.TRACK:
                        if enqueue:
                            self.enqueue_item(clicked-1)
                        else:
                            self.play_uri(clicked-1)
                    else:
                        if enqueue:
                            self.enqueue_folder(self.library[clicked - 1].uri)
                        else:
                            self.go_inside_directory(
                                self.library[clicked - 1].uri, clicked)
            elif touch_event.type != InputManager.key or \
                 touch_event.direction == InputManager.enter:
                self.go_inside_directory(self.library[clicked].uri, clicked)

    def enqueue_item(self, track_pos):
        self.manager.core.tracklist.add(uris = [self.library[track_pos].uri])

    def enqueue_list(self, items):
        uris = []
        for item in items:
            if item.type == mopidy.models.Ref.TRACK:
                uris.append(item.uri)
        self.manager.core.tracklist.add(uris = uris)

    def enqueue_folder(self, uri):
        self.enqueue_list(self.manager.core.library.browse(uri).get())

    def play_uri(self, track_pos):
        self.manager.core.tracklist.clear()
        self.enqueue_list(self.library)
        utils.play_track(self.manager.core, self.library, track_pos)
