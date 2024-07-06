import requests
from bs4 import BeautifulSoup
import time
import fake_useragent
from fastapi import FastAPI

from src.database import session_creation
from src.models import Vacanci
from src.creat import create_tables

app = FastAPI()


ua = fake_useragent.UserAgent()

@app.get("/begin")
def begin(search: str = None, salary: str = None):
    vacancys = {"elements": [], "error": "not_error","city":[]}
    create_tables()
    try:
        for link in get_links(search, salary):
            resume(link)
            time.sleep(3)
        with session_creation() as session:
            vacancys_from_db = session.query(Vacanci).all()
            for one_vacancy_from_db in vacancys_from_db:
                vacancys["elements"].append(
                    {
                        "profession": one_vacancy_from_db.profession,
                        "salary": one_vacancy_from_db.salary,
                        "experience": one_vacancy_from_db.experience,
                        "schedule": one_vacancy_from_db.schedule,
                        "skills": one_vacancy_from_db.skills,
                        "address": one_vacancy_from_db.address,
                        "rating": one_vacancy_from_db.rating,
                        "company": one_vacancy_from_db.company,
                        "link": one_vacancy_from_db.link

                    }

                )
                vacancys["city"].append(one_vacancy_from_db.address)

    except:
        vacancys["error"] = "error_parsing"
    return vacancys


def get_links(search: str = None, salary: str = None):
    if search == None: search = ""
    links=[]
    data=requests.get(
        url=f"https://hh.ru/search/vacancy?text={search}&salary={salary}",
        headers={"user-agent": ua.random}
    )
    soup = BeautifulSoup(data.content ,"lxml")
    try:
        page_max=int(soup.find("div" , class_="pager").find_all("span", recursive=False)[-1].find("a").find("span").text)
        #page_max=int(soup.find("div",class_="pager").find_all("span")[-3].text)

    except:return
    for page in range(page_max):
        try:
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?text={search}&page={page}$salary={salary}",
                headers={"user-agent": ua.random}
            )
            soup = BeautifulSoup(data.content , "lxml")
            for link_in_a in [d.find("a") for d in soup.find_all("span", class_="serp-item__title-link-wrapper")]:
                if "vacancy" in f"{link_in_a.attrs['href'].split('?')[0]}":
                    links.append(f"{link_in_a.attrs['href'].split('?')[0]}")
                if len(links)>=12:
                    return links
        except Exception as e:
            print(f"{e}")
            time.sleep(1)
    else:
        return links
def resume(link):
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    soup = BeautifulSoup(data.content, "lxml")
    with session_creation() as session:
        vacancys = Vacanci()
        try:
            profession_from_parser=soup.find("h1", class_="bloko-header-section-1").text
            vacancys.profession = profession_from_parser
        except:
            return
        try:
            salary_from_parser = soup.find(attrs={
                'data-qa': 'vacancy-salary'}).find("span").text.replace(
                "\xa0", '')
        except:
            salary_from_parser = "Уровень дохода не указан"
        vacancys.salary = salary_from_parser
        try:
            experience_from_parser = soup.find(attrs={"data-qa": "vacancy-experience"}).text
        except:
            experience_from_parser = "Не указан"
        vacancys.experience = experience_from_parser
        try:
            schedule_from_parser = soup.find(attrs={"data-qa": "vacancy-view-employment-mode"}).text
        except:
            schedule_from_parser = "Не указан"
        vacancys.schedule = schedule_from_parser
        skills_from_parser = [skill.find("div", recursive=False).find("div").text for skill in soup.find_all("li", attrs={"data-qa": "skills-element"})]
        if not skills_from_parser:
            skills_from_parser = "Не указаны"
        else:
            skills_from_parser = ", ".join(skills_from_parser)
        vacancys.skills = skills_from_parser
        try:
            region_from_parser = soup.find(attrs={"data-qa": "vacancy-view-location"}).text
            if region_from_parser !="":
                vacancys.address = region_from_parser
        except:
            address_from_parser = soup.find(attrs={"data-qa": "vacancy-view-raw-address"}).text.split(",")[0]
            if address_from_parser !="":
                vacancys.address = address_from_parser
        try:
            rating_from_parser=soup.find(attrs={"data-qa": "employer-review-small-widget-total-rating"}).text
        except:
            rating_from_parser="Не найдено"
        vacancys.rating = rating_from_parser
        try:
            company_from_parser=soup.find(attrs={"data-qa": "bloko-header-2"}).text
        except:
            company_from_parser="Не найдено"
        vacancys.company = company_from_parser
        vacancys.link = link
        session.add(vacancys)
        session.commit()


def for_filters(search: str, colum: str):
    with session_creation() as session:
        mas={
                "experience": Vacanci.experience,
                "schedule": Vacanci.schedule,
                "address": Vacanci.address,

            }
        value = session.query(Vacanci.id, mas[colum]).all()
        idi = []
        for i in value:
            if search in i[1]:
                idi.append(i[0])
        return idi

@app.get("/filtri_vacansi")
def filters(address: str = None, experience: str = None, schedule: str = None):
    correct_id = []
    correct_id1 = set()
    answer = {"elements": [], "error": "not_error","city":[]}
    count = 0
    with session_creation() as session:
        if address:
            norm_regadr_id = for_filters(address, "address")
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
        else:
            vacs = session.query(Vacanci).all()
        for vac in vacs:
            answer["elements"].append(
                {
                    "profession": vac.profession,
                    "salary": vac.salary,
                    "experience": vac.experience,
                    "schedule": vac.schedule,
                    "skills": vac.skills,
                    "address": vac.address,
                    "rating": vac.rating,
                    "company": vac.company,
                    "link": vac.link

                }
            )
            answer["city"].append(vac.address)
    if len(answer["elements"])==0:
        answer["error"]="error_of_filters"
    return answer











