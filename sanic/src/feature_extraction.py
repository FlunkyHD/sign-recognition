import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands

# Python Generator that yields an image every call
def getImagesFromVideo(video):
    cvVideoWrapper = cv2.VideoCapture(video)

    if cvVideoWrapper.isOpened() == False:
        raise Exception("Could not open video")
    
    while cvVideoWrapper.isOpened():
        wasReadSuccess, image = cvVideoWrapper.read()

        if not wasReadSuccess:
            break

        yield image

def getLandmarksFromVideo(video, flipped):
    results = []
    with mp_hands.Hands(
        model_complexity=0,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as MP_HandsTracker:

        for image in getImagesFromVideo(video):
            frame = []
            if flipped:
                image = cv2.flip(image, 1)

            result = MP_HandsTracker.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            for hand_landmarks in result.multi_hand_landmarks:
                for landmark in hand_landmarks.landmark:
                    frame.append({'x': landmark.x, 'y': landmark.y, 'z': landmark.z})
            results.append(frame)

        return results