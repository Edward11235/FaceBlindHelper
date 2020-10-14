from kivy.app import App
from kivy.uix.label import Label
import cv2
from Frame_Face_Recognization import Frame_Face_Recognization
import face_recognition
import time
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import whatimage


class SimpleKivy(App):

    def build(self):
        face_rec = Frame_Face_Recognization()
        video_capture = cv2.VideoCapture(0)
        face_rec.get_encoded_faces()

        while True:
            ret, frame = video_capture.read()
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            img = small_frame[:, :, ::1]
            img = face_rec.classify_faces(img)

            cv2.imshow('result', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return img

        video_capture.release()
        # cv2.destroyAllWindows()
        # return Label(text="Face Detection Application")


if __name__ == "__main__":
    SimpleKivy().run()