from fastapi import FastAPI
from pydantic import BaseModel
from serpapi_parser import fetch


app = FastAPI()


class Request(BaseModel):
    country: str
    query: str


@app.post("/find-deal")
def find_deal(req: Request):
    results = fetch(req.query, req.country)
    return results
