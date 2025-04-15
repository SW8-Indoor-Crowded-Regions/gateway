import bson
from app.test.factories.room_factory import RoomFactory

class SensorFactory():
	def __init__(self,
			id: str = str(bson.ObjectId()),
			rooms: list = [],
			latitude: float = 55.68857313325573,
			longitude: float = 12.57839827681376):
		if not bson.ObjectId.is_valid(id):
			raise ValueError(f"Invalid ObjectId: {id}")
		self.id = id
		self.rooms = rooms or [RoomFactory(), RoomFactory()]
		self.latitude = latitude
		self.longitude = longitude

	def __str__(self) -> str:
		return f"Sensor (id={self.id}, rooms=[{', '.join([room.name for room in self.rooms])}], latitude={self.latitude}, longitude={self.longitude})"
	
	def to_dict(self):
		return {
			'id': self.id,
			'rooms': [room.id for room in self.rooms],
			'latitude': self.latitude,
			'longitude': self.longitude,
		}
