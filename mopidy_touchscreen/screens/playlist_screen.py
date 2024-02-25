from .base_screen import BaseScreen

from ..graphic_utils import ListView
from ..input import InputManager
from .. import utils


class PlaylistScreen(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.list_view = ListView((0, 0), size, self.base_size,
            self.fonts['base'])
        self.playlists_strings = []
        self.playlists = []
        self.selected_playlist = None
        self.playlist_tracks = []
        self.playlist_tracks_strings = []
        self.playlists_loaded()

    def should_update(self):
        return self.list_view.should_update()

    def find_update_rects(self, rects):
        return self.list_view.find_update_rects(rects)


    def update(self, screen, update_type, rects):
        update_all = (update_type == BaseScreen.update_all)
        self.list_view.render(screen, update_all, rects)

    def playlists_loaded(self):
        self.selected_playlist = None
        self.playlists_strings = []
        self.playlists = []
        for playlist in self.manager.core.playlists.as_list().get():
            self.playlists.append(playlist.uri)
            self.playlists_strings.append(playlist.name)
        self.list_view.set_list(self.playlists_strings)

    def playlist_selected(self, playlist):
        self.selected_playlist = playlist
        self.playlist_tracks = self.manager.core.playlists.get_items(playlist).get()
        self.playlist_tracks_strings = ["../"]
        for track in self.playlist_tracks:
            if track.name is None:
                self.playlist_tracks_strings.append(track.uri)
            else:
                self.playlist_tracks_strings.append(track.name)

        self.list_view.set_list(self.playlist_tracks_strings)

    def enqueue_list(self, items):
        self.manager.core.tracklist.add(
            uris = list(map(lambda x: x.uri, items)))

    def touch_event(self, touch_event):
        clicked = self.list_view.touch_event(touch_event,
            (InputManager.enter, InputManager.enqueue, InputManager.back))
        if clicked is not None:
            if touch_event.type == InputManager.key:
                enqueue = touch_event.direction == InputManager.enqueue
                back = touch_event.direction == InputManager.back
            else:
                enqueue = False
                back = False

            if self.selected_playlist is None:
                if enqueue:
                    self.enqueue_list(
                        self.manager.core.playlists.get_items(
                            self.playlists[clicked]).get())
                elif not back:
                    self.playlist_selected(self.playlists[clicked])
            else:
                if back or clicked == 0:
                    self.selected_playlist = None
                    self.list_view.set_list(self.playlists_strings)
                else:
                    if enqueue:
                        self.manager.core.tracklist.add(
                            uris = [self.playlist_tracks[clicked-1].uri])
                    else:
                        self.manager.core.tracklist.clear()
                        self.enqueue_list(self.playlist_tracks)
                        utils.play_track(self.manager.core,
                                         self.playlist_tracks, clicked-1)
