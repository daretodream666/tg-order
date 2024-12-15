from sqlalchemy import create_engine
from sqlalchemy import String, Integer
from sqlalchemy import select, delete
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite+pysqlite:///bot.db", echo=True)

class Teachers(Base): #База данных учителей
    __tablename__ = 'teachers'
    
    id: Mapped[int] = mapped_column(primary_key=True) #tg id
    name: Mapped[str] = mapped_column(String()) #указанное имя
    year: Mapped[int] = mapped_column(Integer()) #курс
    faculty: Mapped[str] = mapped_column(String()) #факультет
    subject : Mapped[str] = mapped_column(String()) #дисциплины
    availability: Mapped[str] = mapped_column(String()) # доступность(даты)
    work_format : Mapped[str] = mapped_column(String()) #формат работы: f2f(очно), remote(дист), both(оба)
    # rating : Mapped[list] = mapped_column(list()) # рейтинг

class Pupils(Base): #База данных учеников
    __tablename__ = 'pupils'
    
    id: Mapped[int] = mapped_column(primary_key=True) #tg id
    name: Mapped[str] = mapped_column(String()) #имя пользователя
    year: Mapped[str] = mapped_column(Integer()) #курс
    faculty: Mapped[str] = mapped_column(String()) #факультет
    subject : Mapped[str] = mapped_column(String()) #дисциплины
    question : Mapped[str] = mapped_column(String()) #запрос
    work_format : Mapped[str] = mapped_column(String()) #формат работы: f2f(очно), remote(дист), both(оба)

def add_teacher(data: dict):
    with Session(engine) as session:
        new_teacher = Teachers(
            id=data["tg_id"],
            name=data["name"],
            year=data["year"],
            faculty=data["faculty"],
            subject=data["subject"],
            availability=data["availability"],
            work_format=data["work_format"]
        )
        session.add(new_teacher)
        session.commit()

def add_pupil(data: dict):
    with Session(engine) as session:
        new_pupil = Pupils(
            id=data["tg_id"],
            name=data["name"],
            year=data["year"],
            faculty=data["faculty"],
            subject=data["subject"],
            question=data["question"],
            work_format=data["work_format"]
        )
        session.add(new_pupil)
        session.commit()

def find_teachers(pupil_id: int):
    with Session(engine) as session:
        pupil_query = select(Pupils).where(Pupils.id == pupil_id)
        pupil = session.execute(pupil_query).scalars().first()

        if not pupil:
            raise ValueError(f"No pupil found with id {pupil_id}")

        pupil_subjects = {s.strip().lower() for s in pupil.subject.split(',')}
        pupil_work_format = pupil.work_format.lower()

        teachers_query = select(Teachers)
        teachers = session.execute(teachers_query).scalars().all()

        suitable_teachers = []
        for teacher in teachers:
            teacher_subjects = {s.strip().lower() for s in teacher.subject.split(',')}
            teacher_work_format = teacher.work_format.lower()

            if pupil_subjects & teacher_subjects and pupil_work_format == teacher_work_format:
                suitable_teachers.append(teacher)

        result = {}

        for teacher in suitable_teachers:
            result[teacher.id] = {
                    "name": teacher.name,
                    "year": teacher.year,
                    "faculty": teacher.faculty,
                    "availability": teacher.availability,
                    "work_format": teacher.work_format,
                    # "rating": teacher.rating
                }
        
            
        return result
    
def get_pupil_data(pupil_id: int):
    with Session(engine) as session:
        pupil_query=select(Pupils).where(Pupils.id == pupil_id)
        pupil = session.execute(pupil_query).scalars().first()

        result = [pupil.name,pupil.year,pupil.faculty,pupil.subject,pupil.question]

        return result
    
def delete_forms_db(tg_id: int):
    with Session(engine) as session:
        session.execute(delete(Pupils).where(Pupils.id == tg_id))
        session.execute(delete(Teachers).where(Teachers.id == tg_id))
        session.execute()