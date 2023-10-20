from fastapi import FastAPI
import httpx
import uvicorn
from app.config.settings import api_settings

app = FastAPI()

# Jikan API base URL
JIKAN_API_URL = 

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

if __name__ == "__main__":

    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)
