
import cv2
import pickle
import face_recognition
import numpy as np

with open("model.pkl", "rb") as file:
    model = pickle.load(file)

camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()

    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)

    for location, encoding in zip(locations, encodings):
        distance = np.linalg.norm(model - encoding)

        recognized = distance < 0.5

        name = "PERSON" if recognized else "UNKNOWN"

        top, right, bottom, left = location

        color = (0, 255, 0) if recognized else (0, 0, 255)

        cv2.rectangle(
            frame, (left, top), (right, bottom), color, 2
        )

        cv2.putText(
            frame,
            f"{name} ({distance:.2f})",
            (left, max(20, top - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    cv2.imshow("Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
