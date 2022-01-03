import os
import io
import cv2
import uvicorn
import numpy as np
import cvlib as cv
from enum import Enum
from cvlib.object_detection import draw_bbox
from starlette.background import BackgroundTask
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse


app = FastAPI()


class Model(str, Enum):
    yolov3tiny = 'yolov3-tiny'
    yolov3 = 'yolov3'


@app.get('/')
def home():
    response = RedirectResponse(url='/docs')
    return response


@app.post('/predict')
def prediction(model: Model, confidence: float=0.5, file: UploadFile = File(...)):
    filename = file.filename
    fileExtension = filename.split('.')[-1] in ('jpg', 'jpeg', 'png')

    if not fileExtension:
        raise HTTPException(
            status_code=415, detail='Unsupported file provided.')

    image_stream = io.BytesIO(file.file.read())
    image_stream.seek(0)
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    bbox, label, conf = cv.detect_common_objects(image, confidence=confidence, model=model)
    output_image = draw_bbox(image, bbox, label, conf)
    cv2.imwrite(f'{filename}', output_image)
    file_image = open(f'{filename}', mode='rb')

    return StreamingResponse(file_image, media_type='image/jpeg', background=BackgroundTask(lambda : os.remove(filename)))

if __name__ == '__main__':
    uvicorn.run(app)
