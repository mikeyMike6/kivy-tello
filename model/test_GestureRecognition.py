import unittest
import cv2
from Enums.Gesture import Gesture
from model.GestureRecognition import GestureRecognition


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = GestureRecognition()


class TestGestureRecognitonThumbUp(TestModel):
    def runTest(self):
        self.thumbUpImg = cv2.imread(r'C:\Users\siwie\Kivy\Lab2\model\fingerup.jpg')
        _, gesture = self.model.recognize_gesture_from(self.thumbUpImg, draw=False)
        self.assertEqual(gesture, Gesture.FINGER_UP)


