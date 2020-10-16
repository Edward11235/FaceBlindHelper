from kivy.app import App
import cv2
from Encoder import Encode
import face_recognition
import time
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.graphics.texture import Texture
import multiprocessing
import numpy as np
from kivy.clock import Clock


class KivyAPP(App):
    def build(self):
        self.img1 = Image()
        layout = FloatLayout()
        layout.add_widget(self.img1)
        self.capture = cv2.VideoCapture(0)
        self.classifyobj = DetectionThread()
        self.routine()
        _, initframe = self.capture.read()
        self.classifyobj.classify_faces(initframe)
        self.recList, self.nameList = self.classifyobj.face_locaions, self.classifyobj.face_names
        # Clock.schedule_interval(self.update, 0.05)
        # Clock.schedule_interval(lambda dt: self.classifyobj.classify_faces(self.img), 1)
        Clock.schedule_interval(self.process1, 0.05)
        Clock.schedule_interval(self.process2, 3)
        return layout

    def process1(self, a):
        proc1 = multiprocessing.Process(target=self.update())
        proc1.start()

    def process2(self, b):
        proc2 = multiprocessing.Process(target=self.classifyobj.classify_faces(self.img))
        proc2.start()

    def routine(self):
        '''读取数据库内的图片和姓名'''
        face_rec = Encode()
        self.encoded = face_rec.get_encoded_faces()
        self.classifyobj.faces_encoded = list(self.encoded.values())
        self.classifyobj.known_face_names = list(self.encoded.keys())

    def update(self):
        '''每次更新读取一次capture.read(),并把传入的长方形框和namelist放如frame中'''
        # cv2 part
        ret, self.img = self.capture.read()
        # self.recList, self.nameList = self.classifyobj.face_locaions, self.classifyobj.face_names

        recList, nameList = self.classifyobj.face_locaions, self.classifyobj.face_names
        for (top, right, bottom, left), name in zip(recList, nameList):
            cv2.rectangle(self.img, (left - 20, top - 20), (right + 20, bottom + 20), (255, 0, 0), 2)

            cv2.rectangle(self.img, (left - 20, bottom - 15), (right + 20, bottom + 20), (255, 0, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.img, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 1)

        # convert it to texture
        buf1 = cv2.flip(self.img, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(self.img.shape[1], self.img.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1

        # Resize frame of video to 1/2 size for faster face recognition processing
        # img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)


# 在 KivyApp class中每隔0.1秒(调整，争取和识别所需时间相同）调用在另一个线程中的Face_recognition。
# Face_recognition return 方框list和name list，在Kivy_app中每隔0.1秒cv2.rectangle一次
class DetectionThread():
    def classify_faces(self, img):
        self.face_locaions = face_recognition.face_locations(img)
        unknown_face_encodings = face_recognition.face_encodings(img, self.face_locaions)
        self.face_names = []

        for f_e in unknown_face_encodings:
            matches = face_recognition.compare_faces(self.faces_encoded, f_e)
            name = 'Unknown'

            face_distances = face_recognition.face_distance(self.faces_encoded, f_e)  # 和faces中各个图片的差距
            best_one = np.argmin(face_distances)
            if matches[best_one]:
                name = self.known_face_names[best_one]
            self.face_names.append(name)

if __name__ == '__main__':
    KivyAPP().run()