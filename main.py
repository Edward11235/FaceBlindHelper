from kivy.app import App
import cv2
from Encoder import Encode
import face_recognition
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty

class MyPopup(Popup):
    input = StringProperty(None)

    def __init__(self, img, rec):
        Popup.__init__(self)
        (x, y, w, h) = rec
        self.image = img[y - 10: y + h + 10, x - 20: x + w + 20]

    def cancel(self):
        cv2.imwrite("./Photo_database/" + self.input+ ".png", self.image)
        self.dismiss()
        KivyAPP.routine()

class ClickableImage(Image):
    faceLo = []
    rectangles = []
    image = None
    nameL = []
    verLength = 0

    def addKnown(self, recs) -> None:
        '''
        The picture argument is a png format picture. This function save the picture
        into photobase folder. the name for the pdf file in the photobase folder is
        name+'.png'.
        '''
        pop = MyPopup(self.image, recs)
        pop.open()

    def on_touch_down(self, touch):
        (a, b) = (touch.x, touch.y)
        for i in range(len(self.rectangles)):
            (x, y, w, h) = self.rectangles[i]
            if x - 10 <= a <= x+w+10 and 720 - (y + h + 10) <= b - (self.verLength -720)/2 <= 720 - (y-10):
                #  print(2)
                if self.nameL[i] == "unknown":
                    self.addKnown(self.faceLo[i])
                    break

class KivyAPP(App):
    def build(self):
        self.imgwidget = ClickableImage()
        self.layout = BoxLayout()
        self.layout.add_widget(self.imgwidget)
        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 720)  #****
        # self.capture.set(4, 1280)  #****
        self.capture.set(4, 1280)
        self.routine()

        self.classify_faces()

        self.recList, self.nameList = self.face_locations, self.face_names
        Clock.schedule_interval(self.update, 0.1)
        Clock.schedule_interval(self.initialize, 0.33)
        return self.layout

    @classmethod
    def routine(self):
        '''读取数据库内的图片和姓名'''
        face_rec = Encode()
        self.encoded = face_rec.get_encoded_faces()
        self.known_face_encodings = list(self.encoded.values())
        self.known_face_names = list(self.encoded.keys())

    def update(self, dt):
        '''每次更新读取一次capture.read(),并把传入的长方形框和namelist放如frame中'''
        ret, self.img = self.capture.read()
        self.img = cv2.resize(self.img, (self.layout.size[0], int(self.layout.size[0]*0.5625)), interpolation=cv2.INTER_CUBIC)
        # self.recList, self.nameList = self.classifyobj.face_locations, self.classifyobj.face_names

        #recList, nameList = self.face_locations, self.face_names

        for (x, y, w, h), name in zip(self.face_locations, self.face_names):
            t = self.layout.size[0] / 1280
            cv2.rectangle(self.img, (int(t*(x))-10, (int(t*(y)))-10), ((int(t*(x + w))) + 10, (int(t*(y + h))) + 10), (0, 255, 0), 2)
            # cv2.rectangle(self.img, (left - 20, top - 20), (right + 20, (bottom + 20), (255, 0, 0), 2)

            cv2.rectangle(self.img, ((int(t*(x))) - 10, (int(t*(y + h))) - 25), ((int(t*(x + w))) + 10, (int(t*(y + h))) + 10), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(self.img, name, ((int(t*(x))) - 10, (int(t*(y + h))) + 5), font, 1.0, (255, 0, 0), 1)

        # convert it to texture
        buf1 = cv2.flip(self.img, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(self.img.shape[1], self.img.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.imgwidget.texture = texture1

    def initialize(self, some):
        self.classify_faces()

    def classify_faces(self):
        _, img = self.capture.read()
        # img = cv2.resize(img, (self.layout.size[0], int(self.layout.size[0]*0.5625)), interpolation=cv2.INTER_CUBIC)
        frame_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cascade_path = "./haarcascade_frontalface_alt2.xml"
        cascade = cv2.CascadeClassifier(cascade_path)
        face_locations = cascade.detectMultiScale(frame_gray, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32))
        nameList = []
        for a in range(len(face_locations)):
            nameList.append('unknown')

        if len(face_locations) > 0:
            for i in range(0, len(face_locations)):
                x, y, w, h = face_locations[i]
                self.imgwidget.rectangles.clear()
                t = self.layout.size[0] / 1280
                self.imgwidget.rectangles.append((int(t*(x))-10, (int(t*(y)))-10, (int(t*(x + w))) + 10, (int(t*(y + h))) + 10))
                image = img[y - 10: y + h + 10, x - 10: x + w + 10]  # 四个返回值（捂脸）
                try:
                    unknown_encoding = face_recognition.face_encodings(image)[0]  #encoding一下准备对比
                except IndexError:
                    continue
                results = face_recognition.compare_faces(self.known_face_encodings, unknown_encoding)

                for j in range(0, len(results)):
                    if results[j] == True:
                        nameList[i] = self.known_face_names[j]  # 若是匹配成功，赋值为该标签
                        break  #成功了就不再for了
        self.face_locations = face_locations
        self.face_names = nameList

        self.imgwidget.faceLo = self.face_locations
        self.imgwidget.verLength = self.layout.size[1]
        self.imgwidget.image = img
        self.imgwidget.nameL = nameList

KivyAPP().run()