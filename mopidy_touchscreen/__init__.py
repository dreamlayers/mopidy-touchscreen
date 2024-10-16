from __future__ import unicode_literals

import os

from mopidy import config, ext

from .touch_screen import TouchScreen


__version__ = '1.0.0'


class Extension(ext.Extension):
    dist_name = 'Mopidy-Touchscreen'
    ext_name = 'touchscreen'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__),
                                 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['screen_width'] = config.Integer(minimum=1)
        schema['screen_height'] = config.Integer(minimum=1)
        schema['resolution_factor'] = config.Integer(minimum=6)
        schema['cursor'] = config.Boolean()
        schema['fullscreen'] = config.Boolean()
        schema['cache_dir'] = config.Path()
        schema['gpio'] = config.Boolean()
        schema['gpio_left'] = config.Integer()
        schema['gpio_right'] = config.Integer()
        schema['gpio_up'] = config.Integer()
        schema['gpio_down'] = config.Integer()
        schema['gpio_enter'] = config.Integer()
        schema['sdl_fbdev'] = config.String()
        schema['sdl_mousdrv'] = config.String()
        schema['sdl_mousedev'] = config.String()
        schema['sdl_audiodriver'] = config.String()
        schema['sdl_path_dsp'] = config.String()
        schema['lirc_socket'] = config.String()
        schema['lirc_remote'] = config.String()
        schema['lirc_pageup'] = config.String()
        schema['lirc_up'] = config.String()
        schema['lirc_down'] = config.String()
        schema['lirc_pagedown'] = config.String()
        schema['lirc_left'] = config.String()
        schema['lirc_right'] = config.String()
        schema['lirc_enter'] = config.String()
        schema['lirc_enqueue'] = config.String()
        schema['lirc_back'] = config.String()
        schema['lirc_repeat'] = config.Integer()
        schema['lcd_timeout'] = config.Integer()
        schema['lcd_socket'] = config.String()

        return schema

    def setup(self, registry):
        registry.add('frontend', TouchScreen)
