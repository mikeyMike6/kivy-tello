from kivy.graphics.texture import Texture
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.clock import Clock
import cv2
import threading
from kivymd.uix.label import MDLabel
from djitellopy import Tello

from Enums.Gesture import Gesture
from Enums.Move import Move
from GestureBuffer import GestureBuffer
from model.GestureRecognition import GestureRecognition
from DroneMovment import Drone

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.connected_with_drone = False
        self.image = None
        self.gesture_rec = None
        self.capture = None
        self.usingBuildInCamera = False
        self.tello = Tello()
        self.movement = Drone(self.tello)
        self.gesture_rec = GestureRecognition()
        self.frame_read = None
        self.buffor = GestureBuffer()

    def build(self):

        layout = MDBoxLayout(orientation='vertical')
        self.image = Image()
        self.droneLabelInfo = MDLabel(
            adaptive_height=True,
            pos_hint={"center_x": .5, "center_y": .5},
            padding=("0dp", "0dp")
        )
        self.label = MDLabel(
            adaptive_height=True,
            pos_hint={"center_x": .5, "center_y": .5},
            padding=("4dp", "4dp")
        )
        layout.add_widget(self.label)
        layout.add_widget(self.droneLabelInfo)
        layout.add_widget(self.image)
        connectButton = MDRaisedButton(
            text='Connect with drone',
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=(None, None)
        )
        connectButton.bind(on_press=self.connect_with_drone)
        layout.add_widget(connectButton)
        startDroneButton = MDRaisedButton(
            text="Click here to start drone",
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=(None, None))
        startDroneButton.bind(on_press=self.start_drone)
        layout.add_widget(startDroneButton)
        landDroneButton = MDRaisedButton(
            text="Click here to land drone",
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=(None, None))
        landDroneButton.bind(on_press=self.land_drone)
        layout.add_widget(landDroneButton)
        Clock.schedule_interval(self.load_video_from_drone, 1.0 / 30.0)
        return layout

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
                self.droneLabelInfo.text = "Unable connect with drone, check WiFi"
            else:
                self.tello.streamon()
                self.frame_read = self.tello.get_frame_read()
                battery = self.tello.get_battery()
                self.droneLabelInfo.text = "Connected with drone, battery is " + str(battery)
                self.connected_with_drone = True

    def load_video_from_drone(self, *args):
        if self.connected_with_drone:
            frame = self.frame_read.frame
            frame, gesture = self.gesture_rec.recognize_gesture_from(frame)
            self.image_frame = frame
            self.label.text = str(gesture)
            buffer = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture
            self.buffor.add_gesture(gesture.value)
            id = self.buffor.get_gesture()
            move = Move(id)
            threading.Thread(target=self.dron_control, args=(move,)).start()
            # self.dron_control(move)

    def video_cam_control(self, *args, **kwargs):
        if self.usingBuildInCamera:
            Clock.schedule_once(self.close_cam)
        else:
            Clock.schedule_once(self.init_cam)

    def init_cam(self, *args, **kwargs):
        self.capture = cv2.VideoCapture(0)
        self.usingBuildInCamera = True

    def close_cam(self, *args, **kwargs):
        self.capture.release()
        self.usingBuildInCamera = False

    def load_video(self, *args):
        if self.usingBuildInCamera:
            status, frame = self.capture.read()
            frame, gesture = self.gesture_rec.recognize_gesture_from(frame)
            self.image_frame = frame
            self.label.text = str(gesture)
            buffer = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture

if __name__ == '__main__':
    MainApp().run()