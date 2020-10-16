from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.core.window import Window
from engine import PlateRecognition
from setting import *


class BestApp(App):

    screen_names = ListProperty([])
    screens = {}  # Dict of all screens
    title = StringProperty()

    def __init__(self, **kwargs):
        self.class_main = PlateRecognition()

        self.title = 'View'

        try:
            Window.size = (960, 540)
            Window.left = 300
            Window.top = 200
        except:
            pass

        super(BestApp, self).__init__(**kwargs)

    # --------------------------- Main Menu Event -----------------------------
    def on_start_capture(self, cam1, cam2, host, database, table, user, password):
        CAM_INFO[0][CAMERA_SOURCE] = cam1
        CAM_INFO[1][CAMERA_SOURCE] = cam2
        self.class_main.process_cameras(host=host, database=database, table=table, user=user, password=password)

    def on_exit(self):
        exit(0)

    def build(self):
        self.load_screen()
        self.go_screen('dlg_menu', 'right')

    def go_screen(self, dest_screen, direction):
        sm = self.root.ids.sm
        sm.switch_to(self.screens[dest_screen], direction=direction)

    def load_screen(self):
        self.screen_names = ['dlg_menu']
        for i in range(len(self.screen_names)):
            screen = Builder.load_file('kv_dlg/' + self.screen_names[i] + '.kv')
            self.screens[self.screen_names[i]] = screen
        return True


if __name__ == '__main__':
    Config.set('graphics', 'resizable', 0)
    BestApp().run()
