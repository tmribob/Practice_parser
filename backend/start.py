import requests
from bs4 import BeautifulSoup
import fake_useragent
from fastapi import FastAPI

from database import session_creation
from models import Vacanci
from creat import create_tables

app = FastAPI()


ua = fake_useragent.UserAgent()

@app.get("/begin")
def begin(search: str = None, salary: str = None):
    vacancys = {"elements": [], "error": "not_error","city":[]}
    create_tables()
    try:
        for link in get_links(search, salary):
            get_vacancy(link)
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
                if len(links)>=30:
                    return links
        except Exception as e:
            print(f"{e}")
    else:
        return links
def get_vacancy(link):
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
        id_comform = []
        for i in value:
            if search in i[1]:
                id_comform.append(i[0])
        return id_comform

@app.get("/filtri_vacansi")
def filters(address: str = None, experience: str = None, schedule: str = None):
    id_filted = []
    correct_id1 = set()
    db_filted = {"elements": [], "error": "not_error","city":[]}
    count = 0
    with session_creation() as session:
        if address:
            id_conform = for_filters(address, "address")
            id_filted += id_conform
            count += 1
        if schedule:
            id_conform = for_filters(schedule, "schedule")
            id_filted += id_conform
            count += 1
        if experience:
            id_conform = for_filters(experience, "experience")
            id_filted += id_conform
            count += 1

        if count != 0:
            for i in id_filted:
                if id_filted.count(i) == count:
                    correct_id1.add(i)
            vacancy_filted = session.query(Vacanci).filter(Vacanci.id.in_(list(correct_id1))).all()
        else:
            vacancy_filted = session.query(Vacanci).all()
        for vacancy in vacancy_filted:
            db_filted["elements"].append(
                {
                    "profession": vacancy.profession,
                    "salary": vacancy.salary,
                    "experience": vacancy.experience,
                    "schedule": vacancy.schedule,
                    "skills": vacancy.skills,
                    "address": vacancy.address,
                    "rating": vacancy.rating,
                    "company": vacancy.company,
                    "link": vacancy.link

                }
            )
            db_filted["city"].append(vacancy.address)
    if len(db_filted["elements"])==0:
        db_filted["error"]="error_of_filters"
    return db_filted











