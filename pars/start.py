import requests
from bs4 import BeautifulSoup
import json
import time
import fake_useragent
from fastapi import FastAPI

from src.database import session_creation
from src.models import Vacanci
from src.creat import create_tables

app = FastAPI()


ua = fake_useragent.UserAgent()

@app.get("/go")
def go(text: str, salary: str = None):
    answer = {"elements": [], "error": "not_error"}
    create_tables()
    try:
        for b in link(text, salary):
            resume(b)
            time.sleep(3)
        with session_creation() as session:
            all_values = session.query(Vacanci).all()
            for alc in all_values:
                answer["elements"].append(
                    {
                        "dolsh": alc.dolsh,
                        "salary": alc.salary,
                        "experience": alc.experience,
                        "schedule": alc.schedule,
                        "skills": alc.skills,
                        "adres": alc.adres

                    }
                )
    except:
        answer["error"]="error_parsing"
    return answer


def link(text: str, salary: str = None):
    linkis=[]
    data=requests.get(
        url=f"https://hh.ru/search/vacancy?text={text}&salary={salary}",
        headers={"user-agent": ua.random}
    )
    soup = BeautifulSoup(data.content,"lxml")
    try:
        page_max=int(soup.find("div",class_="pager").find_all("span", recursive=False)[-1].find("a").find("span").text)
        #page_max=int(soup.find("div",class_="pager").find_all("span")[-3].text)

    except:return
    for i in range(page_max):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?text={text}&page={i}$salary={salary}",
                headers={"user-agent": ua.random}
            )
            soup = BeautifulSoup(data.content, "lxml")
            for b in [d.find("a") for d in soup.find_all("span", class_="serp-item__title-link-wrapper")]:
                if "vacancy" in f"{b.attrs['href'].split('?')[0]}":
                    linkis.append(f"{b.attrs['href'].split('?')[0]}")
                if len(linkis)>=15:
                    return linkis
        except Exception as e:
            print(f"{e}")
            time.sleep(1)
    else:
        return linkis
def resume(text):
    data = requests.get(
        url=text,
        headers={"user-agent": ua.random}
    )
    soup = BeautifulSoup(data.content, "lxml")
    with session_creation() as session:
        vacancies = Vacanci()
        try:
            name=soup.find("h1", class_="bloko-header-section-1").text
            vacancies.dolsh = name
        except:
            return
        try:
            salary = soup.find(attrs={
                'data-qa': 'vacancy-salary'}).find("span").text.replace(
                "\xa0", '')
            vacancies.salary = salary
            time.sleep(1)
        except:
            salary = "Уровень дохода не указан"
            vacancies.salary = salary
        try:
            experience = soup.find(attrs={"data-qa": "vacancy-experience"}).text
            vacancies.experience = experience
        except:
            experience = "Error"
            vacancies.experience = experience
        try:
            schedule = soup.find(attrs={"data-qa": "vacancy-view-employment-mode"}).text
            vacancies.schedule = schedule
        except:
            schedule = "Error"
            vacancies.schedule = schedule
        skills = [skill.find("div", recursive=False).find("div").text for skill in soup.find_all("li", attrs={"data-qa": "skills-element"})]
        if not skills:
            skills = "Error"
            vacancies.skills = skills
        else:
            skills = ", ".join(skills)
            vacancies.skills = skills
        try:
            region = soup.find(attrs={"data-qa": "vacancy-view-location"}).text
            if region !="":
                vacancies.adres = region
        except:
            adres = soup.find(attrs={"data-qa": "vacancy-view-raw-address"}).text
            if adres !="":
                vacancies.adres = adres
        session.add(vacancies)
        session.commit()

        """vacan={
            "dolsh": name,
            "salary": salary,
            "experience": experience,
            "schedule": schedule,
            "skills": skills,
            "region": region,
            "adres": adres
        }
    return vacan"""

def for_filters(search: str, colum: str):
    with session_creation() as session:
        if colum == "regadr":
            value = session.query(Vacanci.id, Vacanci.adres).all()
        elif colum == "experience":
            value = session.query(Vacanci.id, Vacanci.experience).all()
        elif colum == "schedule":
            value = session.query(Vacanci.id, Vacanci.schedule).all()
        idi = []
        for i in value:
            if colum == "regadr":
                if search in i[1] or search in i[2]:
                    idi.append(i[0])
            else:
                if search in i[1]:
                    idi.append(i[0])
        return idi

@app.get("/filtri_vacansi")
def filters(regadr: str = None, experience: str = None, schedule: str = None):
    correct_id = []
    correct_id1 = set()
    answer = {"elements": []}
    count = 0
    with session_creation() as session:
        if regadr:
            norm_regadr_id = for_filters(regadr, "regadr")
            correct_id += norm_regadr_id
            count += 1
        if experience:
            norm_experience_id = for_filters(experience, "experience")
            correct_id += norm_experience_id
            count += 1
        if schedule:
            norm_schedule_id = for_filters(schedule, "schedule")
            correct_id += norm_schedule_id
            count += 1
        if count > 0:
            for i in correct_id:
                if correct_id.count(i) == count:
                    correct_id1.add(i)
            vacs = session.query(Vacanci).filter(Vacanci.id.in_(list(correct_id1))).all()
            for vac in vacs:
                answer["elements"].append(
                    {
                        "dolsh": vac.dolsh,
                        "salary": vac.salary,
                        "experience": vac.experience,
                        "schedule": vac.schedule,
                        "skills": vac.skills,
                        "adres": vac.adres
                    }
                )
        else:
            vacs = session.query(Vacanci).all()
            for vac in vacs:
                answer["elements"].append(
                    {
                        "dolsh": vac.dolsh,
                        "salary": vac.salary,
                        "experience": vac.experience,
                        "schedule": vac.schedule,
                        "skills": vac.skills,
                        "adres": vac.adres
                    }
                )
    return answer











