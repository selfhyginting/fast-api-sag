from data import Base,engine
from models import Item

print("Creating a database...")

Base.metadata.create_all(engine)