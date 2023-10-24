from fastapi import FastAPI,Depends,HTTPException
import httpx
import uvicorn
from .config.settings import api_settings
from sqlalchemy.orm import Session
from . import models, schemas,crud
from .database import SessionLocal, engine
from app.redis import get_redis
import json
from fastapi import BackgroundTasks

models.Base.metadata.create_all(bind=engine)

EX_CACHE = 60

redis = get_redis()


async def set_cache(data, key):
    await redis.set(
        key,
        json.dumps(data),
        ex=EX_CACHE,
    )

async def get_cache(key):
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title=api_settings.TITLE,
    openapi_url=f'{api_settings.PREFIX}/openapi.json',
    docs_url=f'{api_settings.PREFIX}/docs',
)

# Jikan API base URL
JIKAN_API_URL =  api_settings.JIKAN_API_URL
app.router.prefix = api_settings.PREFIX

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/anime")
async def get_anime_info(title: str):
    async with httpx.AsyncClient() as client:
        # Make a GET request to the Jikan API to search for the anime by title https://api.jikan.moe/v4/anime?q=naruto&sfw
        response = await client.get(f"{JIKAN_API_URL}?q={title}&sfw")
        print(f"{JIKAN_API_URL}?q={title}&sfw")
        if response.status_code == 200:
            anime_data = response.json()
            return anime_data
    return {"error": "Anime not found"}


@app.get("/list")
async def get_anime_list(background_tasks: BackgroundTasks,title: str , page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    try:
        key = f'{title}_{page}_{size}'
        data = await get_cache(key)
        if not data:
            print('cache miss')
            animes = crud.get_animes_per_page(db, title, page=page, size=size)
            # print(animes)
            background_tasks.add_task(set_cache, schemas.serialize_response(animes), key)
            return animes
        print('cache hit')
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )