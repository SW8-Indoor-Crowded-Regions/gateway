from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List
from app.schemas.sensor_response_schema import SensorWithRoomsModel


class FrontendPathFindingRequest(BaseModel):
	source: str
	target: str

	@field_validator('source', 'target', mode='before')
	def check_source_and_target(cls, value, info: ValidationInfo):
		if not value or not value.strip():
			raise ValueError(f"Field '{info.field_name}' must be a non-empty string.")
		return value


class FrontendMultiPathRequest(BaseModel):
	source: str
	targets: List[str]
 
	@field_validator('source', mode='before')
	def check_source(cls, value, info: ValidationInfo):
		if not value or not value.strip():
			raise ValueError(f"Field '{info.field_name}' must be a non-empty string.")
		return value

	@field_validator('targets', mode='before')
	def check_targets(cls, value, info: ValidationInfo):
		if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
			raise ValueError(f"Field '{info.field_name}' must be a non-empty list of non-empty strings.")
		return value


class FastestPathModel(BaseModel):
    fastest_path: List[SensorWithRoomsModel]
    distance: float
