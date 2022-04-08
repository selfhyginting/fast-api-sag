from fastapi import FastAPI
from routes import items, users

app = FastAPI()


@app.get('/')
def welcomegreet():
    return "Welcome"

app.include_router(users.router)
app.include_router(items.router)
 