from click import echo
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine=create_engine("postgresql://postgres:yourkey@localhost/item_db",
    echo=True
)

Base=declarative_base()

Session=sessionmaker(bind=engine)