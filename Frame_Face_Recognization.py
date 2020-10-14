import cv2
import face_recognition as fr
import os
import numpy as np
import face_recognition


class Frame_Face_Recognization:

    def get_encoded_faces(self):
        encoded = {}

        for dirpath, dnames, fnames in os.walk("./Photo_database"):
            for f in fnames:
                if f.endswith(".png"):
                    face = fr.load_image_file("Photo_database/" + f)
                    encoding = fr.face_encodings(face)[0]
                    encoded[f.split(".")[0]] = encoding
        return encoded


    def classify_faces(self, img):
        faces = self.get_encoded_faces()
        faces_encoded = list(faces.values())
        known_face_names = list(faces.keys())

        face_locaions = face_recognition.face_locations(img)
        unknown_face_encodings = face_recognition.face_encodings(img, face_locaions)

        face_names = []
        for f_e in unknown_face_encodings:
             matches = face_recognition.compare_faces(faces_encoded, f_e)
             name = 'Unknown'

             face_distances = face_recognition.face_distance(faces_encoded, f_e)  # 和faces中各个图片的差距
             best_one = np.argmin(face_distances)
             if matches[best_one]:
                 name = known_face_names[best_one]

             face_names.append(name)

             for (top, right, bottom, left), name in zip(face_locaions, face_names):
                 cv2.rectangle(img, (left-20, top-20), (right+20, bottom+20), (255, 0, 0), 2)

                 cv2.rectangle(img, (left - 20, bottom - 15), (right + 20, bottom + 20), (255, 0, 0), cv2.FILLED)
                 font = cv2.FONT_HERSHEY_DUPLEX
                 cv2.putText(img, name, (left - 20, bottom + 15), font, 1.0, (255, 255, 255), 1)

        return img
        # while True:
        #     cv2.imshow('result', img)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         return face_names
