from pydantic.v1 import BaseModel


class Anime(BaseModel):
    id: int
    title: str
    url: str

    class Config:
        orm_mode = True


def serialize_anime(anime):
    return {
        "id": anime.id,
        "title": anime.title,
        "url": anime.url
    }


class ResponseAnime(BaseModel):
    data: list[Anime]
    total: int
    page: int
    pages: int
    size: int

def serialize_response(response):
    # print(response)
    return {
        "data": [serialize_anime(anime) for anime in response['data']],
        "total": response['total'],
        "page": response['page'],
        "pages": response['pages'],
        "size": response['size']
    }