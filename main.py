from fastapi import FastAPI, Request, UploadFile, File, Form
from models import InputImage, OutputImage
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates    
from fastapi.responses import HTMLResponse
from converter import Converter_factory
from numpy import frombuffer, uint8, ndarray
from cv2 import imdecode, IMREAD_COLOR, imencode
import base64


app = FastAPI()
#app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(name="base.html", request=request)

@app.post("/convert", response_class=HTMLResponse)
async def convert_image(image: UploadFile = File(...), processing: str = Form(...)):
    cv2_image = await process_image(image)
    converter = Converter_factory(processing)
    result = converter.convert(cv2_image)
    incoded_img = incode_img(result)
    response_html = get_html_resposne(incoded_img)
    return response_html 

async def process_image(image: UploadFile = File(...)) -> ndarray:
    image_data = await image.read()
    nparr = frombuffer(image_data, uint8)
    # Decode the image into a cv2 image (NumPy array)
    img_cv2 = imdecode(nparr, IMREAD_COLOR)
    return img_cv2

def get_html_resposne(image: str | ndarray) -> str:
    if image is str:
        response_html = f'''
            <div>
                <h2>Processed ASCII Art</h2>
                <pre style="white-space: pre-wrap; word-wrap: break-word;">{image}</pre>
            </div>
        '''
    else:
        response_html = f'''
    <div>
        <h2>Processed Image</h2>
        <img src="data:image/jpeg;base64,{image}" style="max-width: 100%; max-height: 400px;">
    </div>
    '''
    return response_html

def incode_img(image: dict): 
    img = image["img"]
    if img is ndarray:
        _, img_encoded = imencode('.jpg', img)
        img_bytes = img_encoded.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return img_base64
    return img