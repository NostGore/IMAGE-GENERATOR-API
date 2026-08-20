from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from generator import ImageGenerator

load_dotenv(Path(__file__).parent / ".env")

DIR = Path(__file__).parent.parent

generator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global generator
    print("Iniciando ImageGenerator...")
    generator = ImageGenerator(headless=True)
    await generator.start()
    print("ImageGenerator listo")
    yield
    await generator.close()


app = FastAPI(title="IMG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    with open(DIR / "index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/generate")
async def generate(prompt: str = Query(..., min_length=1)):
    if generator is None:
        return JSONResponse(content={"success": False, "error": "Servidor no inicializado correctamente"})
    result = await generator.generate(prompt)
    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
