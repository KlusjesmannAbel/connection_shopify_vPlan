from fastapi import APIRouter
import httpx, os
from dotenv import load_dotenv

load_dotenv()

VPLAN_API_KEY = os.getenv("VPLAN_API_KEY")
VPLAN_API_ENV = os.getenv("VPLAN_API_ENV")
VPLAN_API_URL = "https://api.vplan.com/v1"
VPLAN_BOARD_ID = os.getenv("VPLAN_BOARD_ID")
router = APIRouter()



@router.get("/labels")
async def get_labels():
	print(VPLAN_API_ENV, VPLAN_API_KEY)
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

@router.get("/status")
async def get_status():
	async with httpx.AsyncClient() as client:
		res = await client.get(
			f"{VPLAN_API_URL}/board?with=statuses",
			headers={
				"X-Api-Key": VPLAN_API_KEY,
				"X-Api-Env": VPLAN_API_ENV,
				"Content-Type": "application/json"
			}
		)
	if res.status_code != 200:
		return {"error": res.text, "status": res.status_code}
	
	return res.json()

@router.get("/stages")
async def get_stages():
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