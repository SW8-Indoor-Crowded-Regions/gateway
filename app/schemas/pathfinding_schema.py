from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List


class FrontendPathFindingRequest(BaseModel):
	source: str
	target: str

	@field_validator('source', 'target', mode='before')
	def check_source_and_target(cls, value, info: ValidationInfo):
		if not value or not value.strip():
			raise ValueError(f"Field '{info.field_name}' must be a non-empty string.")
		return value


class FastestPathModel(BaseModel):
	fastest_path: List[str]
	distance: float
