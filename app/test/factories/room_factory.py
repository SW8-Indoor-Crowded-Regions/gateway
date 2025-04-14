import bson

class RoomFactory():
	def __init__(self, 
					id: str = str(bson.ObjectId()),
					name: str = "Room 1",
					type: str = "EXHIBITION",
					crowd_factor: float = 0.9,
					popularity_factor: float = 1.1,
					occupants: int = 0,
					area: float = 12.5,
					longitude: float = 12.57839827681376,
					latitude: float = 55.68857313325573,
					sensors: list = [],
					floor: int = 1,
					borders: list = [[55.68857313325573, 12.57839827681376], [55.68857313325573, 12.57839827681376], [55.68857313325573, 12.57839827681376]]
              ):
		if not bson.ObjectId.is_valid(id):
			raise ValueError(f"Invalid ObjectId: {id}")
		self.id = id
		self.name = name
		self.type = type
		self.crowd_factor = crowd_factor
		self.popularity_factor = popularity_factor
		self.occupants = occupants
		self.area = area
		self.longitude = longitude
		self.latitude = latitude
		self.sensors = sensors
		self.floor = floor
		self.borders = borders
	def __str__(self) -> str:
		return f"""Room (id={self.id}, name={self.name}, type={self.type}, occupancy={self.occupants}, crowdFactor={self.crowd_factor}, 
			popularityFactor={self.popularity_factor}, area={self.area}, sensors={["Sensor id: " + sensor.id.__str__() for sensor in self.sensors]})
			latitude={self.latitude}, longitude={self.longitude}, floor={self.floor}, borders={self.borders})"""
   
	def to_dict(self):
		return {
			'id': self.id,
			'name': self.name,
			'type': self.type,
			'crowd_factor': self.crowd_factor,
			'popularity_factor': self.popularity_factor,
			'occupants': self.occupants,
			'area': self.area,
			'longitude': self.longitude,
			'latitude': self.latitude,
			'sensors': [sensor.id for sensor in self.sensors],
			'floor': self.floor,
			'borders': self.borders
		}