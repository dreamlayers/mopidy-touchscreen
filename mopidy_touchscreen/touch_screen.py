import logging
import os
import traceback
from threading import Thread
from threading import Timer
from threading import Lock

from mopidy import core, exceptions

import pygame

import pykka

from .screen_manager import ScreenManager

from .input import LIRCManager
from .input import InputManager
from .input import InputEvent

logger = logging.getLogger(__name__)


class TouchScreen(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(TouchScreen, self).__init__()
        self.core = core
        self.running = False
        self.cursor = config['touchscreen']['cursor']
        self.cache_dir = config['touchscreen']['cache_dir']
        self.fullscreen = config['touchscreen']['fullscreen']
        self.screen_size = (config['touchscreen']['screen_width'],
                            config['touchscreen']['screen_height'])
        self.resolution_factor = (config['touchscreen']['resolution_factor'])
        if config['touchscreen']['sdl_fbdev'].lower() != "none":
            os.environ["SDL_FBDEV"] = config['touchscreen']['sdl_fbdev']
        if config['touchscreen']['sdl_mousdrv'].lower() != "none":
            os.environ["SDL_MOUSEDRV"] = (
                config['touchscreen']['sdl_mousdrv'])

        if config['touchscreen']['sdl_mousedev'].lower() != "none":
            os.environ["SDL_MOUSEDEV"] = config['touchscreen']['sdl_mousedev']

        if config['touchscreen']['sdl_audiodriver'].lower() != "none":
            os.environ["SDL_AUDIODRIVER"] = (
                config['touchscreen']['sdl_audiodriver'])

        os.environ["SDL_PATH_DSP"] = config['touchscreen']['sdl_path_dsp']
        #pygame.init()
        pygame.font.init()
        #pygame.display.set_caption("Mopidy-Touchscreen")
        self.get_display_surface(self.screen_size)
        #pygame.mouse.set_visible(self.cursor)
        self.screen_manager = ScreenManager(self.screen_size,
                                            self.core,
                                            self.cache_dir,
                                            self.resolution_factor)

        # Raspberry pi GPIO
        self.gpio = config['touchscreen']['gpio']
        if self.gpio:

            from .input import GPIOManager

            pins = {}
            pins['left'] = config['touchscreen']['gpio_left']
            pins['right'] = config['touchscreen']['gpio_right']
            pins['up'] = config['touchscreen']['gpio_up']
            pins['down'] = config['touchscreen']['gpio_down']
            pins['enter'] = config['touchscreen']['gpio_enter']
            self.gpio_manager = GPIOManager(pins)

        self.lirc = LIRCManager(fname = config['touchscreen']['lirc_socket'],
                                remote = config['touchscreen']['lirc_remote'],
                                repeat = config['touchscreen']['lirc_repeat'])
        self.lircmap = {
            config['touchscreen']['lirc_up'] : InputManager.up,
            config['touchscreen']['lirc_down'] : InputManager.down,
            config['touchscreen']['lirc_left']: InputManager.left,
            config['touchscreen']['lirc_right']: InputManager.right,
            config['touchscreen']['lirc_enter']: InputManager.enter
        }

        self.timer = None
        self.screen_sleeping = False
        self.lcd_timeout = config['touchscreen']['lcd_timeout']
        self.lcd_lock = Lock()

    def get_display_surface(self, size):
        try:
            self.screen = pygame.Surface(size)
            '''
            if self.fullscreen:
                self.screen = pygame.display.set_mode(
                    size, pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
            '''
        except Exception:
            raise exceptions.FrontendError("Error on display init:\n"
                                           + traceback.format_exc())
    def _timeout(self):
        self.actor_ref.tell("timeout")

    def _start_timer(self, time):
        if self.timer:
            self.timer.cancel()
        if time > 0:
            self.timer = Timer(time, self._timeout)
            self.timer.start()

    def on_receive(self, message):
        if message == "timeout":
            self.lcd_lock.acquire()
            if not self.screen_sleeping:
                self.screen_manager.sleep()
                self.screen_sleeping = True
            self.lcd_lock.release()

    def start_thread(self):
        clock = pygame.time.Clock()
        #pygame.event.set_blocked(pygame.MOUSEMOTION)
        self._start_timer(self.lcd_timeout)
        while self.running:
            clock.tick(12)
            self.lcd_lock.acquire()
            if not self.screen_sleeping:
                self.screen_manager.update(self.screen)

            lirc_keys = self.lirc.get()
            got_keys = False
            for key in lirc_keys:
                mappedkey = self.lircmap.get(key)
                if mappedkey is not None:
                    got_keys = True
                    if self.screen_sleeping:
                        self.screen_sleeping = False
                    else:
                        self.screen_manager.event(InputEvent(InputManager.key,
                                                             None, None, None,
                                                             mappedkey,
                        # keyboard screen fails if if unicode isn't an int
                                                             0,
                                                             longpress=False))
            if got_keys:
                self._start_timer(self.lcd_timeout)
            self.lcd_lock.release()

            '''
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os.system("pkill mopidy")
                elif event.type == pygame.VIDEORESIZE:
                    self.get_display_surface(event.size)
                    self.screen_manager.resize(event)
                else:
                    self.screen_manager.event(event)
            '''
        if self.timer:
            self.timer.cancel()
        self.screen_manager.close()
        pygame.quit()

    def on_start(self):
        try:
            self.running = True
            thread = Thread(target=self.start_thread)
            thread.start()
        except:
            traceback.print_exc()

    def on_stop(self):
        self.running = False

    def track_playback_started(self, tl_track):
        try:
            self.screen_manager.track_started(tl_track)
        except:
            traceback.print_exc()

    def volume_changed(self, volume):
        self.screen_manager.volume_changed(volume)

    def playback_state_changed(self, old_state, new_state):
        self.screen_manager.playback_state_changed(old_state,
                                                   new_state)

    def tracklist_changed(self):
        try:
            self.screen_manager.tracklist_changed()
        except:
            traceback.print_exc()

    def track_playback_ended(self, tl_track, time_position):
        self.screen_manager.track_playback_ended(tl_track,
                                                 time_position)

    def options_changed(self):
        try:
            self.screen_manager.options_changed()
        except:
            traceback.print_exc()

    def playlists_loaded(self):
        self.screen_manager.playlists_loaded()

    def stream_title_changed(self, title):
        self.screen_manager.stream_title_changed(title)
