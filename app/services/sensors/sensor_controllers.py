import os
from dotenv import load_dotenv
from app.utils.forwarder import forward_request
from app.schemas.sensor_response_schemas import SensorModel, SensorListModel
from fastapi import HTTPException

load_dotenv()
SENSOR_SIM_PATH = os.getenv('SENSOR_SIM', 'http://localhost:8002')
if SENSOR_SIM_PATH is None:
	raise RuntimeError('SENSOR_SIM not found in environment variables')

PATHFINDING_PATH = os.getenv('PATHFINDING', 'http://localhost:8001')
if PATHFINDING_PATH is None:
	raise RuntimeError('PATHFINDING not found in environment variables')

async def get_all_sensors() -> SensorListModel:
	res, status = await forward_request(SENSOR_SIM_PATH + '/sensors', 'GET')
	try: 
		SensorListModel.model_validate(res, strict=True)
		return res
	except Exception:
		raise HTTPException(
			status_code=status,
			detail=res.get('detail', 'Invalid room data received from sensor simulation service')
		)
  
async def get_sensor_by_id(sensor_id: str) -> SensorModel:
	res, status = await forward_request(SENSOR_SIM_PATH + f'/sensors/{sensor_id}', 'GET')
  
	try: 
		SensorModel.model_validate(res, strict=True)
		return res
	except Exception:
		raise HTTPException(
			status_code=status,
			detail=res.get('detail', 'Invalid room data received from sensor simulation service')
		)