from fastapi import FastAPI
import httpx
import uvicorn
from app.config.settings import api_settings

app = FastAPI(
    title=api_settings.TITLE,
    openapi_url=f'{api_settings.PREFIX}/openapi.json',
    docs_url=f'{api_settings.PREFIX}/docs',
)

# Jikan API base URL
JIKAN_API_URL =  api_settings.JIKAN_API_URL
app.router.prefix = api_settings.PREFIX

@app.get("/anime")
async def get_anime_info(title: str):
    async with httpx.AsyncClient() as client:
        # Make a GET request to the Jikan API to search for the anime by title https://api.jikan.moe/v4/anime?q=naruto&sfw
        response = await client.get(f"{JIKAN_API_URL}?q={title}&sfw")
        print(response.status_code)
        if response.status_code == 200:
            anime_data = response.json()
            if "results" in anime_data:
                # Return the first result
                if len(anime_data["results"]) > 0:
                    return anime_data["results"][0]
    return {"error": "Anime not found"}

def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )