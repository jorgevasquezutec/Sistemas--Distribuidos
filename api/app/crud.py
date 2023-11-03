from sqlalchemy.orm import Session
from app import models, schemas


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
    # anime equal
    query = db.query(models.Anime).filter(models.Anime.title == title)
    if not query.count():
        return None
    return query.first()

    # query = db.query(models.Anime).filter(models.Anime.title.ilike(f'%{title}%'))