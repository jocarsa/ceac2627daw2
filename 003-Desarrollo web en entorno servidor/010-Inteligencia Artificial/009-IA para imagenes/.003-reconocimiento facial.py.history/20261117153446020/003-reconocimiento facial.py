# pip3 install face_recognition opencv-python numpy --break-system-packages


import os
import pickle
import numpy as np
import face_recognition

folder = "training/person"
encodings = []

for filename in os.listdir(folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(folder, filename)

        image = face_recognition.load_image_file(path)
        faces = face_recognition.face_encodings(image)

        if len(faces) == 1:
            encodings.append(faces[0])
            print("Trained:", filename)

if not encodings:
    raise RuntimeError("No valid faces found")

model = np.mean(encodings, axis=0)

with open("model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Training completed:", len(encodings), "photos")
