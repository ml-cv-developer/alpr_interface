from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.core.window import Window
from engine import PlateRecognition


class BestApp(App):

    screen_names = ListProperty([])
    screens = {}  # Dict of all screens
    title = StringProperty()
    txt_video1_file = StringProperty()
    txt_video2_file = StringProperty()
    txt_key1_file = StringProperty()
    txt_key2_file = StringProperty()

    def __init__(self, **kwargs):
        self.class_main = PlateRecognition()

        self.title = 'View'
        self.text_index = 0


        try:
            Window.size = (960, 540)
            Window.left = 300
            Window.top = 200
        except:
            pass

        super(BestApp, self).__init__(**kwargs)

    # --------------------------- Main Menu Event -----------------------------
    def go_file(self, index):
        self.title = 'Select File'
        self.text_index = index
        self.go_screen('dlg_file', 'left')

    def on_file_select(self, state, value):
        self.title = 'View'
        self.go_screen('dlg_menu', 'right')
        if state == 'sel':
            if self.text_index == 0:
                self.txt_video1_file = value[0]
            elif self.text_index == 1:
                self.txt_key1_file = value[0]
            elif self.text_index == 2:
                self.txt_video2_file = value[0]
            elif self.text_index == 3:
                self.txt_key2_file = value[0]

    def on_exit(self):
        exit(0)

    # ----------------------- Processing Event ---------------------------
    def on_compare_video(self, video_name1, keypoint_name1, video_name2, keypoint_name2):
        pass

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
