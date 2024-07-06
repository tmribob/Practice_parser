from database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Vacanci(Base):
    __tablename__ = "vakansii"

    id: Mapped[int] = mapped_column(primary_key=True)
    profession: Mapped[str]
    salary: Mapped[str]
    experience: Mapped[str]
    schedule: Mapped[str]
    skills: Mapped[str]
    address: Mapped[str]
    rating: Mapped[str]
    company: Mapped[str]
    link: Mapped[str]
