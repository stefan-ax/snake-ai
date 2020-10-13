from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

app.mount("/game", StaticFiles(directory="game"), name="game")
templates = Jinja2Templates(directory="game")


@app.get("/", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Entrypoint for local testing
if __name__ == "__main__":
    uvicorn.run(app)
