import os
import httpx
import time
from fastapi import FastAPI
from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from routers import utils

load_dotenv()
app = FastAPI()

VPLAN_API_KEY = os.getenv("VPLAN_API_KEY")
VPLAN_API_ENV = os.getenv("VPLAN_API_ENV")
VPLAN_API_URL = "https://api.vplan.com/v1"
VPLAN_BOARD_ID = os.getenv("VPLAN_BOARD_ID")
FLOW_COMPANION_URL = "https://flow-companion.mivicle.app/rest/1/flow/start/order"
FLOW_COMPANION_TOKEN = os.getenv("FLOW_COMPANION_TOKEN")

app.include_router(utils.router, prefix="/utils", tags=["utils"])

class IntegrationRequest(BaseModel):
	name: str
	description: str = ""
	due_date: str = ""
	order_id: str = ""
	has_corpus: bool = False

@app.post("/vplan/integration")
async def integration(request: IntegrationRequest):
	labels = []
	if "Maatwerk kleur (kies later)" in request.description or "Verkeerswit (RAL9016)" in request.description or "Gitzwart (RAL9005)" in request.description:
		labels.append({"id":"a1fd731c-b9f9-49c2-be93-58562910ee7b"})
	elif "Zuiver wit (RAL9010)" in request.description:
		labels.append({"id":"ad6d0814-4768-4304-81f6-e6b20e588dc0"})
	elif "Schilderklaar" in request.description:
		labels.append({"id":"6bc00e21-7778-4b0f-bed9-87aa8ec2d87c"})
	if request.has_corpus:
		labels.append({"id":"e5eb7b93-8893-4391-bc95-0ac40c887675"})
	payload = {
		"name": request.name,
		"description": request.description,
		"labels": labels,
		"custom_fields": [{"name": "shopify_id","type":"text", "value":request.order_id, "priority": 0}],
		"board_id": VPLAN_BOARD_ID,
		"due_date": request.due_date
	}

	#create collection
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

	time.sleep()
	#put the collection to the board
	payload = {}
	async with httpx.AsyncClient() as client:
		res = await client.post(
			f"{VPLAN_API_URL}/collection/{data['id']}/board/{VPLAN_BOARD_ID}",
			headers={
				"X-Api-Key": VPLAN_API_KEY,
				"X-Api-Env": VPLAN_API_ENV,
				"Content-Type": "application/json"
			},
			json=payload
		)
	
	print(res)
	if res.status_code not in [200, 201]:
		return {"error": res.text, "status": res.status_code}
	
	#return collection_id to shopify
	companion_body = {
			"itemId": request.order_id,
			"specifier": "vPlan collection gemaakt",
			"additionalParameters": {
			"stringParameter": data["id"]
		}
	}

	async with httpx.AsyncClient() as client:
		res = await client.post(
			FLOW_COMPANION_URL,
			headers={
				"Authorization": f"Bearer {FLOW_COMPANION_TOKEN}",
				"Content-Type": "application/json"
			},
			json=companion_body
		)
