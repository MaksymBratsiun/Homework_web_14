import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.routes import contacts, auth, users

app = FastAPI()

origins = [
    "http://localhost:3000", "http://127.0.0.1:3000"
]


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    such as connecting to databases or initializing caches.

    :return: A list of coroutines
    :doc-author: Trelent
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    The root function returns a JSON object with the message 'Contact book'.

    :return: A dict, which is converted into json
    :doc-author: Trelent
    """
    return {"message": "Contact book"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple endpoint that returns a JSON object with the message 'All right!'
    if everything is working correctly. This function can be used to check if the API server and database are up and
    running.

    :param db: Session: Pass the database session to the function
    :return: A json object with the message “all right!”
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "All right!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix='/api')

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
