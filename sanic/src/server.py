from sanic import Sanic, json
from sanic.response import text, HTTPResponse
from sanic.request import Request
from sanic_ext import openapi
from pathlib import Path
import numpy as np
import feature_extraction as fe
import tempfile
import os
import utils

model = utils.load_model(os.path.join("models", "test")) #TODO fix whhen there is a model
feature_extractor = utils.build_feature_extractor() #TODO Fjern hvis den ikke skal bruges

SIGN_LIST = ['book', 'dog', 'fish', 'help', 'man', 'movie', 'pizza', 'woman'] #TODO Check om rækkefølgen stadig passer med ny model

app = Sanic("MortenIsCringeApp")
app.config.CORS_ORIGINS = "*"

@app.get("/")
async def hello_world(request):
    return text("Hello, world.")

@app.post("/api/hands")
@openapi.parameter("flip", bool, description="Whether the video is flipped.")
async def hands(request: Request) -> HTTPResponse:
    """
    Send a video and recieve hand keypoints for every frame. 
    openapi:
    operationId: hands
    tags:
      - Mediapipe
    parameters:
      - name: flip
        in: query
        type: boolean
    requestBody:
        content:
            multipart/form-data:
                schema:
                    type: object
                    properties:
                        video:
                            type: string
                            format: binary
    responses:
      '200':
        description: Returns json object which is an array of frames. Every frame has a left and a right hand accociated,
                    where every hand has 21 landmarks with x, y, z coordinates
        content:
            application/json: {}
    """
    flipped = request.args.get("flip")
    videofile = request.files.get("video")

    with tempfile.NamedTemporaryFile() as temp:

        temp.write(videofile.body) # write the video into a temporary file
        return json(fe.getLandmarksFromVideo(temp.name, flipped), 200)

@app.post("/api/savevideo")
@openapi.parameter("label", str, description="The label of the sign which is used for saving it the correct place")
async def savevideo(request: Request) -> HTTPResponse:
    """
    Save the video on the server
    openapi:
    operationId: savevideo
    tags: 
      - SaveVideo
    parameters:
      - name: label
        in: query
        type: string
    requestBody:
        content:
            multipart/form-data:
                schema:
                    type: object
                    properties:
                        video:
                            type: string
                            format: binary
    responses:
      '200':
        description: returns 200 on successful save
    """
        
    label = request.args.get("label")
    videofile = request.files.get("video")

    if (label != ""):
        currentdir = os.path.dirname(__file__)
        video_dir_path = os.path.join(currentdir, f"./videos/{label}")

        Path(f"{video_dir_path}").mkdir(parents=True, exist_ok=True) # Creates the directory ./videos/{label} recursively if they don't exists

        file = open(f"{video_dir_path}/{request.id}.mp4", "wb")
        file.write(videofile.body)
        file.close()
        return text("Succesfully saved file", 200)
    else:
        return text("No label provided!", 400)

@app.post("/api/predict")
@openapi.parameter("label", str, description="The label of the sign which is used for saving it the correct place")
async def predict_video(request: Request) -> HTTPResponse:
    """
    Predict sign from video
    openapi:
    operationId: predict_video
    tags:
      - Predict sign
    requestBody:
        content:
            multipart/form-data:
                schema:
                    type: object
                    properties:
                        video:
                            type: string
                            format: binary
    responses:
      '200':
        description: returns 200 on successful prediction attempt by model
    """
        
    videofile = request.files.get("video")


    with tempfile.NamedTemporaryFile() as temp:
        temp.write(videofile.body) # write the video into a temporary file
        video = np.array(utils.load_video(temp.name))

     # Expand dims size the model expects a list of videos and not just a video
    fixed_size = np.expand_dims(video, axis=0)
    prediction = model.predict(fixed_size)

    # Find index of the max value
    max_value_index = np.argmax(prediction)

    # Create object to be returned
    returnObject = dict()
    returnObject["prediction"] = SIGN_LIST[max_value_index]

    # Nested list. First element, because it is only 1 video (and can accept multiple)
    all_predictions = prediction.tolist()[0]
    prediction_objects = []

    # Combining predictions (floats) with their sign. Otherwise a duplicate SIGN_LIST would be needed on frontend
    for index, sign in enumerate(SIGN_LIST):
        prediction_objects.append({ all_predictions[index], sign })

    returnObject["predictionObjects"] = prediction_objects

    return json(returnObject, 200)