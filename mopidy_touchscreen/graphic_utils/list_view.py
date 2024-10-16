import logging

from .screen_objects import ScreenObjectsManager, ScrollBar, \
    TouchAndTextItem

from ..input import InputManager

logger = logging.getLogger(__name__)


class ListView():
    def __init__(self, pos, size, base_size, font):
        self.size = size
        self.pos = pos
        self.base_size = base_size
        self.screen_objects = ScreenObjectsManager()
        self.max_rows = self.size[1] // font.size("TEXT SIZE")[1]
        self.current_item = 0
        self.font = font
        self.list_size = 0
        self.list = []
        self.scrollbar = False
        self.selected = None
        self.active = []
        self.set_list([])
        self.update_keys = []
        self.update_once = []
        self.update_all = False
        self.rect = self.pos + self.size

    # Sets the list for the lisview.
    # It should be an iterable of strings
    def set_list(self, item_list):
        self.screen_objects.clear()
        self.list = item_list
        self.list_size = len(item_list)
        if self.max_rows < self.list_size:
            self.scrollbar = True
            scroll_bar = ScrollBar(
                (self.pos[0] + self.size[0] - self.base_size,
                 self.pos[1]),
                (self.base_size, self.size[1]), self.list_size,
                self.max_rows)
            self.screen_objects.set_touch_object("scrollbar",
                                                 scroll_bar)
        else:
            self.scrollbar = False
        if self.list_size > 0:
            self.selected = 0
        else:
            self.selected = None
        self.load_new_item_position(0)

    # Will load items currently displaying in item_pos
    def load_new_item_position(self, item_pos):
        self.update_keys = []
        self.update_once = []
        self.current_item = item_pos
        if self.scrollbar:
            self.screen_objects.clear_touch(["scrollbar"])
        else:
            self.screen_objects.clear_touch(None)
        i = self.current_item
        z = 0
        if self.scrollbar:
            width = self.size[0] - self.base_size
        else:
            width = self.size[0]
        current_y = self.pos[1]
        while i < self.list_size and current_y <= self.pos[1] + self.size[1]:
            item = TouchAndTextItem(self.font, self.list[i], (
                self.pos[0],
                current_y), (width, -1))
            current_y += item.size[1]
            if not item.fit_horizontal:
                self.update_keys.append(str(i))
            self.screen_objects.set_touch_object(str(i), item)
            i += 1
            z += 1
        self.reload_selected()
        self.update_all = True

    def add_update_once(self, key):
        skey = str(key)
        if skey not in self.update_keys:
            self.update_once.append(skey)

    def should_update(self):
        if self.update_all or len(self.update_keys) > 0 or \
           len(self.update_once) > 0:
            return True
        else:
            return False

    def find_update_rects(self, rects):
        if self.update_all:
            rects.append(self.rect)
        else:
            for key in self.update_keys + self.update_once:
                object = self.screen_objects.get_touch_object(key)
                rects.append(object.rect_in_pos)

    def render(self, surface, update_all, rects):
        if update_all or self.update_all:
            self.screen_objects.render(surface)
        else:
            for key in self.update_keys + self.update_once:
                object = self.screen_objects.get_touch_object(key)
                object.update()
                object.render(surface)
        self.update_once = []
        self.update_all = False

    def touch_event(self, touch_event, accept_keys = (InputManager.enter,)):
        if touch_event.type == InputManager.click \
                or touch_event.type == InputManager.long_click:
            objects = self.screen_objects.get_touch_objects_in_pos(
                touch_event.current_pos)
            if objects is not None:
                for key in objects:
                    if key == "scrollbar":
                        direction = \
                            self.screen_objects.get_touch_object(
                                key).touch(touch_event.current_pos)
                        if direction != 0:
                            self.move_to(direction)
                    else:
                        return int(key)
        elif (touch_event.type == InputManager.key and
                self.selected is not None):
            if touch_event.direction in accept_keys:
                if self.selected is not None:
                    return self.selected
            elif touch_event.direction == InputManager.up:
                self.set_selected(self.selected-1)
            elif touch_event.direction == InputManager.down:
                self.set_selected(self.selected+1)
        elif touch_event.type == InputManager.swipe:
            if touch_event.direction == InputManager.up:
                self.page_move(-1)
            elif touch_event.direction == InputManager.down:
                self.page_move(1)

    # Scroll to direction
    # direction == 1 will scroll down
    # direction == -1 will scroll up
    def move_to(self, direction):
        if self.scrollbar:
            if direction == 1:
                self.current_item += self.max_rows
                if self.current_item + self.max_rows > self.list_size:
                    self.current_item = self.list_size - self.max_rows
                self.load_new_item_position(self.current_item)
                self.screen_objects.get_touch_object(
                    "scrollbar").set_item(
                    self.current_item)
            elif direction == -1:
                self.current_item -= self.max_rows
                if self.current_item < 0:
                    self.current_item = 0
                self.load_new_item_position(self.current_item)
                self.screen_objects.get_touch_object(
                    "scrollbar").set_item(
                    self.current_item)
            self.set_active(self.active)

    def page_move(self, direction):
        last_current = self.current_item
        self.move_to(direction)

        if last_current == self.current_item:
            if direction == -1:
                self.set_selected(0)
            elif direction == 1:
                self.set_selected(self.list_size - 1)
        else:
            self.set_selected(self.selected + self.current_item - last_current)

    # Set active items
    def set_active(self, active):
        for number in self.active:
            try:
                self.screen_objects.get_touch_object(
                    str(number)).set_active(
                    False)
                self.add_update_once(number)
            except KeyError:
                pass
        for number in active:
            try:
                self.screen_objects.get_touch_object(
                    str(number)).set_active(
                    True)
                self.add_update_once(number)
            except KeyError:
                pass
        self.active = active

    def set_selected(self, selected):
        if selected > -1 and selected < len(self.list):
            if self.selected is not None:
                try:
                    self.screen_objects.get_touch_object(
                        str(self.selected)).set_selected(
                        False)
                    self.add_update_once(self.selected)
                except KeyError:
                    pass
            if selected is not None:
                try:
                    self.screen_objects.get_touch_object(
                        str(selected)).set_selected(
                        True)
                    self.add_update_once(selected)
                except KeyError:
                    pass
            self.selected = selected
            self.set_selected_on_screen()

    def set_selected_on_screen(self):
        if self.current_item + self.max_rows <= self.selected:
            self.move_to(1)
            self.set_selected_on_screen()
        elif self.current_item > self.selected:
            self.move_to(-1)
            self.set_selected_on_screen()

    def reload_selected(self):
        if self.selected is not None:
            try:
                self.screen_objects.get_touch_object(
                    str(self.selected)).set_selected(
                        True)
            except KeyError:
                pass
