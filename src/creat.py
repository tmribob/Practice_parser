from src.database import Base, engine


def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("\033[91m {}\033[00m".format("huo"))