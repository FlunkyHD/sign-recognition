import base64
import json
import os
import cv2
import requests
from requests import Response

TEST_OPENPOSE = True
TEST_3DCNN = False

TEST_DATASET_PATH = "/the_test/"

def append_to_log(msg: str):
    file_object = open('/sendvideo/video/sendinglog.txt', 'a')
    file_object.write(msg)

# Converts a base64 bytes file to its blob string representation
def convert_base64_to_string_format(b64, type):
    b64_string = str(b64)
    return f'data:{type};base64,{b64_string[2:len(b64_string)-1]}'

def extract_frames_from_video(video_path):
    sequence = []

    # Create OpenCV capture using video as src
    capture = cv2.VideoCapture(video_path)
    # Check if capture opened successfully
    if (capture.isOpened() == False):
        raise Exception("Error opening video file.")
    # Read frames until video is completed
    while capture.isOpened():
        # Capture every frame
        ret, frame = capture.read()
        if ret:
            sequence.append(frame)

        # Break the loop when no more frames
        else:
            break
    # When all frames are extracted, release the video capture object
    capture.release()
    # Close all the OpenCV window frames
    cv2.destroyAllWindows()

    return sequence

def test_openpose():

    correct = 0 # Counter for correct guesses
    tested = 0 # Counter for amount tested

    # Iterate over all subfolders to get all videos and send to openpose
    for subdir, dirs, files in os.walk(TEST_DATASET_PATH):
        for file in files:
            filepath = os.path.join(subdir, file)
            if(filepath == f"{TEST_DATASET_PATH}.gitignore"):
                continue
            frames = extract_frames_from_video(filepath)

            valid_base64_data = []
            for frame in frames:
                ret, buffer = cv2.imencode('.jpg', frame)
                b64 = base64.b64encode(buffer)
                valid_base64_data.append(convert_base64_to_string_format(b64, 'image/jpg'))

            # sending get request and saving the response as response object
            r: Response = requests.post(url="http://localhost:5000/recognize", data=json.dumps(valid_base64_data))

            if("/the_test/" + r.text == subdir):
                correct += 1
            tested += 1

            print(f"Sent: {filepath} and got response: {r.status_code} {r.reason} {r.text}. Amount tested: {tested} Amount correctly guessed: {correct}. That is {correct / tested * 100}%")
            append_to_log(f"Sent file {filepath} and recieved prediction {r.text}. Amount tested: {tested} Amount correctly guessed: {correct}. That is {correct / tested * 100}% acc so far\n")

def test_our_service():
    # Iterate over all subfolders to get all videos and send to sanic
    for subdir, dirs, files in os.walk(TEST_DATASET_PATH):
        for file in files:
            filepath = os.path.join(subdir, file)
            if(filepath == f"{TEST_DATASET_PATH}.gitignore"):
                continue

            # sending get request and saving the response as response object
            file = {'video': open(filepath, 'rb')}
            r: Response = requests.post(url="http://sanic:8000/api/predict", files=file)

            print(f"Sent: {filepath} and got response: {r.status_code} {r.reason} {r.text}.")


if TEST_OPENPOSE:
    test_openpose()
if TEST_3DCNN:
    test_our_service()