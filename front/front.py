import time

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from fastapi import FastAPI, Form
import requests
import os
from fastapi.staticfiles import StaticFiles

c=0

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
         search: str = Form(default=None),
         salary: str = Form(default=None),
         address: str = Form(default=None),
         experience: str = Form(default=None),
         schedule: str = Form(default=None)):
    global global_answer , c
    if path_variable == "parsing":
        params = {
            "search": search,
            "salary": salary
        }
        server_response = requests.get("http://back:7419/begin", params=params)
        global_answer = server_response

    if path_variable == "Filters":
        params = {
            "address": address ,
            "experience": experience,
            "schedule": schedule
        }
        server_response = requests.get("http://back:7419/filtri_vacansi", params=params)
        global_answer = server_response
    time.sleep(1)
    data = global_answer.json()
    page_max = len(data["elements"])//6+(len(data["elements"])%6+5)//6
    if path_variable == "left":
        if c>0:
            c-=1
    if path_variable == "right":
        if c<page_max-1:
            c+=1
    return templates.TemplateResponse("vacancy.html", {"request": request, "data":data["elements"], "error": data["error"],"city": set(data["city"]), "page":c, "max_page":page_max})