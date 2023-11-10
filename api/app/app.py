from fastapi import FastAPI,Depends,HTTPException
# import httpx
import uvicorn
from .config.settings import api_settings
from sqlalchemy.orm import Session
from . import models, schemas,crud
from .database import SessionLocal, engine
# from app.redis import get_redis
import json
# from fastapi import BackgroundTasks
import circuitbreaker
import requests
from app.config.celery_utils import create_celery,get_task_info
from celery import shared_task
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

# EX_CACHE = 60

# redis = get_redis()


class MyCircuitBreaker(circuitbreaker.CircuitBreaker):
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 60
    EXPECTED_EXCEPTION = requests.RequestException

# async def set_cache(data, key):
#     await redis.set(
#         key,
#         json.dumps(data),
#         ex=EX_CACHE,
#     )

# async def get_cache(key):
#     data = await redis.get(key)
#     if data:
#         return json.loads(data)
#     return None

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

app.celery_app = create_celery()

celery = app.celery_app

# Jikan API base URL
JIKAN_API_URL =  api_settings.JIKAN_API_URL
app.router.prefix = api_settings.PREFIX


# @shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
#              name='celery:insert_anime_task')
# def insert_anime_task(self,anime : schemas.Anime):
#     with SessionLocal() as db:
#         crud.add_anime(db,anime)
#         return {"status": "success"}
    
@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
 name='celery:insert_anime_task')
def insert_anime_task(self,title : str):
    animes = get_anime_info(title)
    if(len(animes) > 0):
        with SessionLocal() as db:
            crud.addChunkAnime(db,animes)
            return {"status": "success", "message": f"Success insert {len(animes)} data of title {title}"}
    


@app.get("/")
async def root():
    return {"message": "API is running"}

def get_anime_info(title: str):
    response = requests.get(f"{JIKAN_API_URL}?q={title}&sfw")
    # print(response.status_code)
    if response.status_code == 200:
        data = response.json()
        return [ 
            schemas.Anime(id=anime['mal_id'],
                          title=anime['title'],
                          url=anime['url']) for anime 
                          in data["data"]
                          ]
    raise HTTPException(status_code=500, detail="Failed get data from jikan")


@MyCircuitBreaker()
def get_anime_info_cc(title: str):
    return get_anime_info(title)

@celery.task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          request.id, exc, traceback))


@app.get("/task/{task_id}")
async def get_task_status(task_id: str)-> dict:
    return get_task_info(task_id)


# @app.get("/anime-test")
# async def anime_test():
#     anime = schemas.Anime(id=2,title="Naruto",url="https://api.jikan.moe/v4/anime/20")
#     # with SessionLocal() as db:
#     #     crud.add_anime(db,anime)
#     task = insert_anime_task.apply_async(args=[anime],link_error=error_handler.s())
#     return JSONResponse({"task_id": task.id})


@app.get("/anime")
def implement_circuit_breaker(title: str,db: Session = Depends(get_db)):
    notInDb = False
    try:
        # print("get data from db")
        data = crud.get_animes(db,title)
        if(len(data) == 0):
            # print("get data from jikan")
            data = get_anime_info_cc(title)
        return {
            "status_code": 200,
            "success": True,
            "message": "Success get data", 
            "data": data
        }
    except circuitbreaker.CircuitBreakerError as e:
        if(notInDb):
            print("queue task")
            task = insert_anime_task.apply_async(
                args=[title],
                link_error=error_handler.s(),
                countdown= 60)                                                 
            return  {
                "status_code": 503,
                "success": False,
                "message": f"Circuit breaker active: {e} with task id {task.id}"
            }
        return {
        "status_code": 503,
        "success": False,
        "message": f"Circuit breaker active: {e}"
        }
    except requests.exceptions.ConnectionError as e:
        return {
        "status_code": 500,
        "success": False,
        "message": f"Failed get starwars data: {e}"
        }



# @app.get("/list")
# async def get_anime_list(background_tasks: BackgroundTasks,title: str , page: int = 1, size: int = 10, db: Session = Depends(get_db)):
#     try:
#         key = f'{title}_{page}_{size}'
#         data = await get_cache(key)
#         if not data:
#             print('cache miss')
#             animes = crud.get_animes_per_page(db, title, page=page, size=size)
#             # print(animes)
#             background_tasks.add_task(set_cache, schemas.serialize_response(animes), key)
#             return animes
#         print('cache hit')
#         return data
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail=str(e))


def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )