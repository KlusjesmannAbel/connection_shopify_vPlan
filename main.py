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

ACT_CNC_WIT = os.getenv("ACT_CNC_WIT")
ACT_ZIJKANTEN_SCHUREN = os.getenv("ACT_ZIJKANTEN_SCHUREN")
ACT_ACHTERKANTEN_PLAKKEN = os.getenv("ACT_ACHTERKANTEN_PLAKKEN")
ACT_CONTROLE_VOOR_GROND = os.getenv("ACT_CONTROLE_VOOR_GROND")
ACT_GRONDLAK = os.getenv("ACT_GRONDLAK")
ACT_DROGEN_GRONDLAK = os.getenv("ACT_DROGEN_GRONDLAK")
ACT_TUSSENSCHUREN = os.getenv("ACT_TUSSENSCHUREN")
ACT_AFLAK = os.getenv("ACT_AFLAK")
ACT_DROGEN_AFLAK = os.getenv("ACT_DROGEN_AFLAK")
ACT_QC_EINDLAAG = os.getenv("ACT_QC_EINDLAAG")
ACT_ACHTERKANTEN_SCHUREN = os.getenv("ACT_ACHTERKANTEN_SCHUREN")
ACT_INPAKKEN_LAKWERK = os.getenv("ACT_INPAKKEN_LAKWERK")
ACT_ASSEMBLAGE = os.getenv("ACT_ASSEMBLAGE")
ACT_QC_ASSEMBLAGE = os.getenv("ACT_QC_ASSEMBLAGE")
ACT_CNC_ZWART = os.getenv("ACT_CNC_ZWART")


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
	activities = []
	if "Maatwerk kleur (kies later)" in request.description or "Gitzwart (RAL9005)" in request.description:
		act_to_add = [
			{"id": ACT_CNC_WIT, "time":40},
			{"id": ACT_ZIJKANTEN_SCHUREN, "time":20},
			{"id": ACT_ACHTERKANTEN_PLAKKEN, "time":60},
			{"id": ACT_CONTROLE_VOOR_GROND, "time":5},
			{"id": ACT_GRONDLAK, "time":40},
			{"id": ACT_DROGEN_GRONDLAK, "time":0},
			{"id": ACT_TUSSENSCHUREN, "time":40},
			{"id": ACT_AFLAK, "time":60},
			{"id": ACT_DROGEN_AFLAK, "time":0},
			{"id": ACT_QC_EINDLAAG, "time":10},
			{"id": ACT_ACHTERKANTEN_SCHUREN, "time":20},
			{"id": ACT_INPAKKEN_LAKWERK, "time":40}
		]
		activities.extend(act_to_add)
	elif "Zuiver wit (RAL9010)" in request.description or "Verkeerswit (RAL9016)" in request.description or "Signaalwit (RAL 9003)" in request.description:
		act_to_add = [
			{"id": ACT_CNC_WIT, "time":40},
			{"id": ACT_ZIJKANTEN_SCHUREN, "time":20},
			{"id": ACT_CONTROLE_VOOR_GROND, "time":5},
			{"id": ACT_GRONDLAK, "time":40},
			{"id": ACT_DROGEN_GRONDLAK, "time":0},
			{"id": ACT_TUSSENSCHUREN, "time":40},
			{"id": ACT_AFLAK, "time":60},
			{"id": ACT_DROGEN_AFLAK, "time":0},
			{"id": ACT_QC_EINDLAAG, "time":10},
			{"id": ACT_ACHTERKANTEN_SCHUREN, "time":20},
			{"id": ACT_INPAKKEN_LAKWERK, "time":40}
		]
		activities.extend(act_to_add)
	elif "Schilderklaar" in request.description:
		act_to_add = [
			{"id": ACT_CNC_WIT, "time":40},
			{"id": ACT_ZIJKANTEN_SCHUREN, "time":20},
			{"id": ACT_CONTROLE_VOOR_GROND, "time":5},
			{"id": ACT_INPAKKEN_LAKWERK, "time":40}
		]
		activities.extend(act_to_add)
	if request.has_corpus:
		act_to_add = [
			{"id": ACT_CNC_ZWART, "time":60},
			{"id": ACT_ASSEMBLAGE, "time":60},
			{"id": ACT_QC_ASSEMBLAGE, "time":5}
		]
		activities.extend(act_to_add)
	payload = {
		"name": request.name,
		"description": request.description,
		"labels": labels,
		"activities":activities,
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
