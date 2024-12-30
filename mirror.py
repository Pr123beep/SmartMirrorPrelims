import cv2
from fer import FER
import pyttsx3
import imutils
import time
import threading
import queue
import random

#initializations hai yahan saari 
detector = FER(mtcnn=True)
engine = pyttsx3.init()
speech_queue = queue.Queue() #lag due to tts avoid krne ke liye hai yeh

COMPLIMENTS = {
    'happy': [
        "Your smile lights up the room!",
        "You look absolutely radiant today!",
        "Your happiness is infectious!"
    ],

    'sad': [
        "You've got this, keep going!",
        "Stay strong, brighter days are ahead!",
        "Don't worry, better times are coming!"
    ],
    'angry': [
        "Take a deep breath, you're doing great!",
        "Stay positive, everything will be fine!",
        "Keep calm, you've handled tough situations before!"
    ],
    'surprise': [
        "Your energy is contagious!",
        "You bring excitement wherever you go!",
        "Your enthusiasm is inspiring!"
    ],
    'fear': [
        "Stay strong, brighter days are ahead!",
        "You're braver than you believe!",
        "Face your fears, you've got the strength!"
    ],
    'disgust': [
        "Your style is impeccable!",
        "You have a great sense of aesthetics!",
        "Your taste is outstanding!"
    ],
}


def get_compliment(emotion):
    return random.choice(COMPLIMENTS.get(emotion, ["You look great today!"]))


def tts_worker(speech_q):
    while True:
        compliment = speech_q.get()
        if compliment is None:
            break
        engine.say(compliment)
        engine.runAndWait()
        speech_q.task_done()


def main():
    threading.Thread(target=tts_worker, args=(speech_queue,), daemon=True).start()

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)
    last_time = 0
    delay = 5
    last_compliment = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

        if len(faces) > 0:
            x, y, w, h = faces[0]
            roi = frame[y:y + h, x:x + w]
            emotions = detector.detect_emotions(roi)
            if emotions:
                scores = emotions[0]["emotions"]
                emotion = max(scores, key=scores.get)
                compliment = get_compliment(emotion)

                cv2.putText(frame, f'Emotion: {emotion.capitalize()}', (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                cv2.putText(frame, compliment, (x, y + h + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                current_time = time.time()
                if (current_time - last_time > delay) and (compliment != last_compliment):
                    speech_queue.put(compliment)
                    last_time = current_time
                    last_compliment = compliment
            #camera rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        else:
            cv2.putText(frame, "No face detected.", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Smart Mirror', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    speech_queue.put(None)


if __name__ == "__main__":
    main()
