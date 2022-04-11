import uvicorn
from fastapi import FastAPI
from routes import items, users

app = FastAPI()


@app.get('/')
def welcomegreet():
    return "Welcome"

app.include_router(users.router)
app.include_router(items.router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8080, reload=True, debug=True)