from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Vacanci(Base):
    __tablename__ = "vakansii"

    id: Mapped[int] = mapped_column(primary_key=True)
    dolsh: Mapped[str]
    salary: Mapped[str]
    experience: Mapped[str]
    schedule: Mapped[str]
    skills: Mapped[str]
    adres: Mapped[str]
    rating: Mapped[str]
    company: Mapped[str]
    link: Mapped[str]
