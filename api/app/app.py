from fastapi import FastAPI,Depends,HTTPException,Request
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


class AnimeExeption(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)



class MyCircuitBreaker(circuitbreaker.CircuitBreaker):
    FAILURE_THRESHOLD = 20
    RECOVERY_TIMEOUT = 60
    EXPECTED_EXCEPTION = AnimeExeption


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

@app.exception_handler(AnimeExeption)
async def anime_exception_handler(request: Request, exc: AnimeExeption):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! Rate limit Jikan."},
    )


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
    if response.status_code == 200:
        data = response.json()
        return [ 
            schemas.Anime(id=anime['mal_id'],
                          title=anime['title'],
                          url=anime['url']) for anime 
                          in data["data"]
                          ]
    raise AnimeExeption()


@MyCircuitBreaker()
def get_anime_info_cc(title: str):
    #print current failer count
    # print(f"Failure count: {get_anime_info_cc._fail_counter}")
    return get_anime_info(title)

@celery.task
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          request.id, exc, traceback))


@app.get("/task/{task_id}")
async def get_task_status(task_id: str)-> dict:
    return get_task_info(task_id)

mcontador = 0

@app.get("/anime")
def implement_circuit_breaker(title: str,db: Session = Depends(get_db)):
    global mcontador
    notInDb = False
    try:
        data = crud.get_animes(db,title)
        # print(data)
        if(len(data) == 0):
            notInDb = True
            # print("not in db")
            data = get_anime_info_cc(title)
            return data
        return data
    except circuitbreaker.CircuitBreakerError as e:
        mcontador=0
        if(notInDb):
            # if(not exist_pending_task_with_title(title)):
                # si ya existe una tarea programa con title ya no lo creas.
            task = insert_anime_task.apply_async(
                args=[title],
                link_error=error_handler.s(),
                countdown= 60)
            message = f"Circuit breaker active: {e} with task id {task.id}"
            raise HTTPException(status_code=503, detail=message)                                      
        raise HTTPException(status_code=503,detail=f"Circuit breaker active: {e}")
    except AnimeExeption as e:
        mcontador = mcontador + 1
        print(f"Cantidad de errors {mcontador}")
        raise HTTPException(status_code=503, detail=f'Oops! Rate limit Jikan.')
    

def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )