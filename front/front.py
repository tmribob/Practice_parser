from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from fastapi import FastAPI, Form
import requests
import os
from fastapi.staticfiles import StaticFiles


otv = FastAPI()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
st_abs_file_path_templates = os.path.join(script_dir, "templates/")
otv.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")
templates = Jinja2Templates(directory=st_abs_file_path_templates)

@otv.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@otv.post("/move/{path_variable}", response_class=HTMLResponse)
def take(request: Request,
         path_variable: str,
         text: str = Form(default=None),
         salary: str = Form(default=None),
         adres: str = Form(default=None),
         experience: str = Form(default=None),
         schedule: str = Form(default=None)):
    global global_answer
    if path_variable == "parsing":
        params = {
            "text": text,
            "salary": salary
        }
        server_response = requests.get("http://127.0.0.1:7419/go", params=params)
        global_answer = server_response

    if path_variable == "Filters":
        params = {
            "adres": adres ,
            "experience": experience,
            "schedule": schedule
        }
        server_response = requests.get("http://127.0.0.1:7419/filtri_vacansi", params=params)
        global_answer = server_response
    data = global_answer.json()
    return templates.TemplateResponse("vacancy.html", {"request": request, "data":data["elements"], "error": data["error"]})