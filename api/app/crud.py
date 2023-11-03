from sqlalchemy.orm import Session
from app import models, schemas



def add_anime(db:Session, anime: schemas.Anime):
    db_anime = models.Anime(id=anime.id,title=anime.title, url=anime.url)
    db.add(db_anime)
    db.commit()
    db.refresh(db_anime)
    # return db_anime


def get_animes_per_page(db: Session, title: str = None, page: int = 1, size: int = 10):
    skip = (page - 1) * size
    # print(title)
    query = db.query(models.Anime)
    if title:
        query = query.filter(models.Anime.title.ilike(f'%{title}%'))
    total = query.count()
    data = query.offset(skip).limit(size).all()
    data = [schemas.Anime.from_orm(anime) for anime in data]
    return {
        "data": data,
        "total": total,
        "page": page,
        "pages": total // size + 1 if total % size > 0 else total // size,
        "size": size
    }

def get_anime(db:Session, title: str):
    query = db.query(models.Anime).filter(models.Anime.title.ilike(f'{title}'))
    print(query.count())
    if query.count() > 0:
        return schemas.serialize_anime(query.first())
    return None