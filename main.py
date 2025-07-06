from fastapi import FastAPI
from pydantic import BaseModel
from serpapi_parser import fetch


app = FastAPI()


class Request(BaseModel):
    country: str
    query: str


@app.post("/")
def find_deal(req: Request):
    results = fetch(req.query, req.country)
    return results


@app.get("/")
def root():
    return {"message": "Welcome to the FindMyDeal API. Use POST / to find deals."}
