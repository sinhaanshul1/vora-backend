import random
from fastapi import FastAPI
from pydantic import BaseModel
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# load_dotenv(override=True)

url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(url, key)
response = (
    supabase.table("Snippets")
    .select("*")
    .execute()
)

# print(response)


# class Snippets(Base):
#     __tablename__ = "snippets"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, unique = True)
#     author = Column(String)
#     text = Column(String, unique = True)
#     # date = Column(Date)

class SnippetCreate(BaseModel):
    # id: int
    title: str
    author: str
    text: str
    tags: list[str]
    embedding: list[float]
    # date: Date



# Create tables

app = FastAPI()

@app.get('/snippets')
def get_users():
    
    # users = db.query(Snippets).all()
    responses = (
    supabase.table("Snippets")
    .select("*")
    .execute()
)

    return responses

@app.post('/snippets')
def new_snippet(snippet: SnippetCreate):
    print(snippet.embedding[:5])
    response = (
    supabase.table("Snippets")
    .insert(snippet.model_dump())
    .execute()
    )
    return snippet

@app.get('/snippets/similar')
def get_similar_snippet(id: str, limit: int):
    res = supabase.rpc(
        "get_similar_snippets_by_id",
        {"snippet_id": id, "k": limit}
    ).execute()
    new_data = []
    for d in res.data:
        new_data.append({'id': d["id_new"], "title": d["title_new"], "author": d["author_new"], "text": d["text_new"], "created_at": d["created_at_new"]})
    return new_data

@app.get('/snippets')
def get_snippet_by_id(id: str):
    response = (
        supabase
        .table("Snippets")
        .select("*")
        .eq("id", id)
        .single()
        .execute()
    )


    return response.data

@app.get('/snippets/random')
def get_random_snippet():
    
    # Step 1: get total count
    count_resp = supabase.table("Snippets").select("id", count="exact").execute()
    total = count_resp.count

    if total == 0:
        return {"error": "No rows in table"}

    # Step 2: pick random offset
    offset = random.randint(0, total - 1)

    # Step 3: fetch row at that offset
    row_resp = (
        supabase.table("Snippets")
        .select("*")
        .range(offset, offset)
        .execute()
    )

    return row_resp.data[0]