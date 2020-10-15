import cv2
import face_recognition as fr
import os
import numpy as np
import face_recognition
import threading


class Encode():

    def get_encoded_faces(self):
        encoded = {}

        for dirpath, dnames, fnames in os.walk("./Photo_database"):
            for f in fnames:
                if f.endswith(".png"):
                    face = fr.load_image_file("Photo_database/" + f)
                    encoding = fr.face_encodings(face)[0]
                    encoded[f.split(".")[0]] = encoding
        return encoded