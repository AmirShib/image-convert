from fastapi import FastAPI, Request
from models import InputImage, OutputImage
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates    
from fastapi.responses import HTMLResponse

app = FastAPI()
#app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(name="base.html", request=request)


