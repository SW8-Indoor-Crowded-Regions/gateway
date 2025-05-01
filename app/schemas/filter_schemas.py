from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List

class Filter(BaseModel):
   key: str
   count: int

class FilterResponse(BaseModel):
	type: str
	filters: List[Filter]

	@field_validator('type')
	def validate_type(cls, value: str, info: ValidationInfo) -> str:
		"""Validate the type field."""
		valid_types = ['creator', 'materials']
		if value not in valid_types:
			raise ValueError(f"Invalid type '{value}'. Must be one of " + valid_types.__str__() + ".")
		return value