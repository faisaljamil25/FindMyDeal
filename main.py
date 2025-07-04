from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Request(BaseModel):
    country: str
    query: str


@app.post("/find-deal")
def find_deal(request: Request):
    return [
        {
            "link": "https://apple.com/iphone16",
            "price": "999",
            "currency": "USD",
            "productName": "Apple iPhone 16 Pro",
        }
    ]
