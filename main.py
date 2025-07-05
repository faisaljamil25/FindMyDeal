from fastapi import FastAPI
from pydantic import BaseModel
from serpapi_parser import fetch


app = FastAPI()


class Request(BaseModel):
    country_code: str
    query: str


@app.post("/find-deal")
def find_deal(req: Request):
    results = fetch(req.query, req.country_code)
    return results
