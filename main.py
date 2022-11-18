from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.clock import Clock
import cv2
import threading
from kivymd.uix.label import MDLabel
from djitellopy import Tello

from Enums.Move import Move
from GestureBuffer import GestureBuffer
from model.GestureRecognition import GestureRecognition
from DroneMovment import Drone


class MainApp(MDApp):

    def __init__(self, **kwargs):
        ## ANDROID DZIALA NA JAVIE WIEC TE ZMIANE =NONE TRZEBA JAKOS ZAMIENIC
        ## NP DLA INT self.int = NumericProperty(0)

        self.connected_with_drone = False
        self.capture = None
        self.usingBuildInCamera = False
        self.frame_read = None
        self.tello = Tello()
        self.movement = Drone(self.tello)
        self.gesture_rec = GestureRecognition()
        self.buffor = GestureBuffer()
        super(MainApp, self).__init__(**kwargs)

    def build(self):

        self.layout = MDBoxLayout()
        self.image = Image()
        self.drone_label_info = MDLabel()
        self.label = MDLabel()
        self.connect_button = MDRaisedButton()
        self.start_drone_button = MDRaisedButton()
        self.land_drone_button = MDRaisedButton()
        self.layout.orientation = 'vertical'

        self.drone_label_info.adaptive_height = True
        self.drone_label_info.pos_hint = {"center_x": .5, "center_y": .5}
        self.drone_label_info.padding = ("0dp", "0dp")
        self.label.adaptive_height = True
        self.label.pos_hint = {"center_x": .5, "center_y": .5}
        self.label.padding = ("4dp", "4dp")

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.drone_label_info)
        self.layout.add_widget(self.image)

        self.connect_button.text = 'Connect with drone'
        self.connect_button.pos_hint = {'center_x': .5, 'center_y': .5}
        self.connect_button.size_hint = (None, None)

        self.connect_button.bind(on_press=self.connect_with_drone)
        self.layout.add_widget(self.connect_button)
        self.start_drone_button.text = "Click here to start drone"
        self.start_drone_button.pos_hint = {'center_x': .5, 'center_y': .5}
        self.start_drone_button.size_hint = (None, None)
        self.start_drone_button.bind(on_press=self.start_drone)

        self.layout.add_widget(self.start_drone_button)
        self.land_drone_button.text = "Click here to land drone"
        self.land_drone_button.pos_hint = {'center_x': .5, 'center_y': .5}
        self.land_drone_button.size_hint = (None, None)
        self.land_drone_button.bind(on_press=self.land_drone)
        self.layout.add_widget(self.land_drone_button)
        Clock.schedule_interval(self.load_video_from_drone, 1.0 / 30.0)
        return self.layout

    def dron_control(self, gesture):
        self.movement.movement(gesture)

    def start_drone(self, *args, **kwargs):
        if self.connected_with_drone and not self.movement.in_air:
            threading.Thread(target=self.movement.start, args=()).start()

    def land_drone(self, *args, **kwargs):
        if self.connected_with_drone and self.movement.in_air:
            threading.Thread(target=self.movement.land, args=()).start()

    def connect_with_drone(self, *args, **kwargs):
        if not self.connected_with_drone:
            try:
                self.tello.connect()
            except:
                self.drone_label_info.text = "Unable connect with drone, check WiFi"
            else:
                self.tello.streamon()
                self.frame_read = self.tello.get_frame_read()
                battery = self.tello.get_battery()
                self.drone_label_info.text = "Connected with drone, battery is " + str(battery)
                self.connected_with_drone = True

    def load_video_from_drone(self, *args):
        if self.connected_with_drone:
            frame = self.frame_read.frame
            frame, gesture = self.gesture_rec.recognize_gesture_from(frame)
            self.label.text = str(gesture)
            buffer = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture
            self.buffor.add_gesture(gesture.value)
            move = Move(self.buffor.get_gesture())
            # threading.Thread(target=self.dron_control, args=(move,)).start()


if __name__ == '__main__':
    MainApp().run()