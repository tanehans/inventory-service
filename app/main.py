from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return { "Hello": "World", "v": "0.5" }


@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}
