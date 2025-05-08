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
			raise ValueError(
				f"Invalid type '{value}'. Must be one of " + valid_types.__str__() + '.'
			)  # pragma: no cover
		return value

	def to_dict(self) -> dict:
		"""Convert the FilterResponse to a dictionary."""
		return { # pragma: no cover
			'type': self.type,
			'filters': [{'key': f.key, 'count': f.count} for f in self.filters],
		}


class FilterRequest(BaseModel):
	type: str
	keys: list[str]


class FilterToRoomsRequest(BaseModel):
	filters: List[FilterRequest]

	@field_validator('filters')
	def validate_filters(
		cls, value: List[FilterRequest], info: ValidationInfo
	) -> List[FilterRequest]:
		"""Validate the filters field."""
		if not value or not isinstance(value, list):
			raise ValueError('Filters must be a non-empty list.') # pragma: no cover
		return value


class FilterToRoomsResponse(BaseModel):
	rooms: List[str]

	@field_validator('rooms')
	def validate_rooms(cls, value: List[str], info: ValidationInfo) -> List[str]:
		"""Validate the rooms field."""
		if not value or not isinstance(value, list): # pragma: no cover
			raise ValueError('Rooms must be a non-empty list.') # pragma: no cover
		return value # pragma: no cover
