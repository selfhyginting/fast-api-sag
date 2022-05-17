from click import echo
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os 
from dotenv import load_dotenv
load_dotenv('.env')

engine=create_engine(os.getenv('CONFIG'),
    echo=True
)

Base=declarative_base()

Session=sessionmaker(bind=engine)