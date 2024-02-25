from .base_screen import BaseScreen

from .main_screen import MainScreen
from ..graphic_utils import ListView
from ..input import InputManager


class Tracklist(BaseScreen):
    def __init__(self, size, base_size, manager, fonts):
        BaseScreen.__init__(self, size, base_size, manager, fonts)
        self.size = size
        self.base_size = base_size
        self.manager = manager
        self.list_view = ListView((0, 0), size, self.base_size, self.fonts['base'])
        self.tracks = []
        self.tracks_strings = []
        self.update_list()
        track = self.manager.core.playback.get_current_tl_track().get()
        if track is not None:
            self.track_started(track)
        self.active = None
        self.selected = None

    def should_update(self):
        return self.list_view.should_update()

    def find_update_rects(self, rects):
        return self.list_view.find_update_rects(rects)


    def update(self, screen, update_type, rects):
        update_all = (update_type == BaseScreen.update_all)
        self.list_view.render(screen, update_all, rects)

    def tracklist_changed(self):
        self.update_list()
        if self.selected:
            if self.active:
                self.track_started(self.active)
            self.list_view.set_selected(self.selected)
            self.selected = None

    def update_list(self):
        self.tracks = self.manager.core.tracklist.get_tl_tracks().get()
        self.tracks_strings = []
        for tl_track in self.tracks:
            self.tracks_strings.append(
                MainScreen.get_track_name(tl_track.track))
        self.list_view.set_list(self.tracks_strings)

    def touch_event(self, touch_event):
        # Kludge to avoid events before the list has been updated after deletion
        if self.selected:
            return
        pos = self.list_view.touch_event(touch_event,
            (InputManager.enter, InputManager.enqueue))
        if pos is not None:
            tlid = self.tracks[pos].tlid
            if touch_event.type == InputManager.key and \
               touch_event.direction == InputManager.enqueue:
                if self.active and self.active.tlid == tlid:
                    if pos < len(self.tracks) - 1:
                        # TODO: Is there a race condition here,
                        # if the next track already started?
                        self.manager.core.playback.next()
                    else:
                        self.manager.core.playback.stop()
                self.selected = min(pos, len(self.tracks) - 2)
                self.manager.core.tracklist.remove({'tlid': [tlid]})
            else:
                self.manager.core.playback.play(tlid = tlid)

    def track_started(self, track):
        self.active = track
        self.list_view.set_active(
            [self.manager.core.tracklist.index(tlid = track.tlid).get()])
