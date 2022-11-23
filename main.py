import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Todo(BaseModel):
    id: int
    task: str


todos: List[Todo] = []


@app.post("/todos/", response_model=Todo)
async def add_todo(todo: Todo):
    todos.append(todo)
    return todo


@app.get("/todos/", response_model=List[Todo])
async def list_todos():
    return todos


@app.delete("/todos/{todo_id}", response_model=Todo)
async def delete_todo(todo_id: int):
    for todo in todos:
        if todo.id == todo_id:
            todos.remove(todo)
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def serve_ai_plugin():
    manifest_path = os.path.join(os.path.dirname(__file__), "manifest.json")
    try:
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
        return JSONResponse(content=manifest_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Manifest file not found")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Simple TODO App",
        version="1.0.0",
        description="A simple TODO app using FastAPI",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
