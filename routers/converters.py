
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from converter import Converter_factory
from numpy import frombuffer, uint8, ndarray
from cv2 import imdecode, IMREAD_COLOR, imencode
import base64

router = APIRouter()

@router.post("/converters/")
async def convert_image(file: UploadFile, style: str = Form(...)):
    try:
        cv2_image = await process_image(file)
        response_html = await _convert(cv2_image, style)
        return HTMLResponse(response_html) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




async def _convert(image: ndarray, style: str):
    factory = Converter_factory(style)
    converter = factory()
    result = converter.convert(image)
    
    if style != "ascii": 
        response = get_html_resposne(incode_img(result))
    else: 
        response = get_ascii_html_response(result)
    
    return response


async def process_image(image: UploadFile = File(...)) -> ndarray:
    image_data = await image.read()
    nparr = frombuffer(image_data, uint8)
    # Decode the image into a cv2 image (NumPy array)
    img_cv2 = imdecode(nparr, IMREAD_COLOR)
    return img_cv2

def get_html_resposne(image: str) -> str:
    response_html = f'''
    <div class="result-container">
        <h2 class="result">Processed Image</h2>
        <img src="data:image/jpeg;base64,{image}" style="max-width: 100%; max-height: 400px;">
        <button class="again" onclick="window.location.href = '/'">Convert another image</button>
        <a class="download" href="data:image/jpeg;base64,{image}" download="processed_image.jpg">Download Image</a>
    </div>
    '''
    return response_html

def get_ascii_html_response(image:str) -> str:
    response_html = f'''
            <div class="result-container">
                <h2 class="result">Processed ASCII Art</h2>
                <pre style="white-space: pre-wrap; word-wrap: break-word; color: gray;">{image}</pre>
                <button class="again" onclick="window.location.href = '/'">Convert another image</button>
                <a class="download"  href="data:image/jpeg;base64,{image}" download="processed_image.jpg">Download Image</a>
            </div>
        '''
    return response_html

def incode_img(image: ndarray) -> str:
    
    _, img_encoded = imencode('.jpg', image)
    img_bytes = img_encoded.tobytes()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return img_base64
    
    