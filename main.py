from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates  
from routers import converters



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(converters.router)
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(name="base.html", request=request)





