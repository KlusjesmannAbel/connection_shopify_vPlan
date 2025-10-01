import os
import httpx
from fastapi import FastAPI
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

VPLAN_API_KEY = os.getenv("VPLAN_API_KEY")
VPLAN_API_ENV = os.getenv("VPLAN_API_ENV")
VPLAN_API_URL = "https://api.vplan.com/v1"
VPLAN_BOARD_ID = "b2a7c932-b55d-4fef-b3b1-825fe6ea477f"

class Label(BaseModel):
	id: str

class CollectionRequest(BaseModel):
	name: str
	description: Optional[str] = ""
	labels : List[Label] = []

@app.post("/vplan/create-collection")
async def create_collection(request: CollectionRequest):
    payload = {
        "name": request.name,
        "description": request.description,
        "labels": [label.model_dump() for label in request.labels],
				"custom_fields": [{"name": "shopify_id","type":"text", "value":"ID", "priority": 0}],
        "board_id": VPLAN_BOARD_ID
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{VPLAN_API_URL}/collection",
            headers={
                "X-Api-Key": VPLAN_API_KEY,
                "X-Api-Env": VPLAN_API_ENV,
                "Content-Type": "application/json"
            },
            json=payload
        )

    if res.status_code not in [200, 201]:
        return {"error": res.text, "status": res.status_code}

    data = res.json()
    return {"collection_id": data.get("id"), "labels": payload["labels"]}


@app.put("/vplan/update-collection/{collection_id}")
async def create_collection(collection_id: str, request: List[Label]):
	print(request)
	payload = {
		"labels": [label.model_dump() for label in request],
	}

	async with httpx.AsyncClient() as client:
		res = await client.put(
			f"{VPLAN_API_URL}/collection/{collection_id}",
			headers={
				"X-Api-Key": VPLAN_API_KEY,
				"X-Api-Env": VPLAN_API_ENV,
				"Content-Type": "application/json"
			},
			json=payload
		)

	if res.status_code not in [200, 201]:
		return {"error": res.text}
	return res.json()

@app.get("/vplan/labels")
async def get_labels():
	async with httpx.AsyncClient() as client:
		res = await client.get(
			f"{VPLAN_API_URL}/board?with=labels",
			headers={
				"X-Api-Key": VPLAN_API_KEY,
				"X-Api-Env": VPLAN_API_ENV,
				"Content-Type": "application/json"
			}
		)
	if res.status_code != 200:
		return {"error": res.text, "status": res.status_code}
	
	return res.json()

@app.get("/vplan/status")
async def get_labels():
	async with httpx.AsyncClient() as client:
		res = await client.get(
			f"{VPLAN_API_URL}/board?with=stages",
			headers={
				"X-Api-Key": VPLAN_API_KEY,
				"X-Api-Env": VPLAN_API_ENV,
				"Content-Type": "application/json"
			}
		)
	if res.status_code != 200:
		return {"error": res.text, "status": res.status_code}
	
	return res.json()

class MoveCollectionToBoard(BaseModel):
	status_id: str

# @app.put("/vplan/put_on_board/{collection_id}")
# async def put_collection_on_board(collection_id: str, request: List[Label]):
# 	async with httpx.AsyncClient() as client:
# 		res = await client.put(
# 			f"{VPLAN_API_URL}/collection/{collection_id}",
# 			headers={
# 				"X-Api-Key": VPLAN_API_KEY,
# 				"X-Api-Env": VPLAN_API_ENV,
# 				"Content-Type": "application/json"
# 			},
# 			json=payload
# 		)

# 	if res.status_code not in [200, 201]:
# 		return {"error": res.text}
# 	return res.json()
