get_sensor_by_id_responses: dict[int | str, dict[str, object]] = {
	200: {
		'description': 'Successful Response',
		'content': {
			'application/json': {
				'example': {
					'id': '123',
					'rooms': ['room_1_id', 'room_2_id'],
					'latitude': 55.6887823848,
					'longitude': 12.57792893289,
					'is_vertical': True,
				}
			}
		},
	},
	400: {
		'description': 'Invalid Sensor ID',
		'content': {'application/json': {'example': {'detail': 'Invalid Sensor ID'}}},
	},
	404: {
		'description': 'Sensor not found',
		'content': {'application/json': {'example': {'detail': 'Sensor not found'}}},
	},
	500: {
		'description': 'Internal Server Error',
		'content': {'application/json': {'example': {'detail': 'Internal Server Error'}}},
	},
}

get_sensors_responses: dict[int | str, dict[str, object]] = {
	200: {
		'description': 'Successful Response',
		'content': {
			'application/json': {
				'example': [
					{
						'id': '123',
						'rooms': ['room_1_id', 'room_2_id'],
						'latitude': 55.6887823848,
						'longitude': 12.57792893289,
						'is_vertical': True,
					},
					{
						'id': '124',
						'rooms': ['room_1_id', 'room_2_id'],
						'latitude': 55.6887823848,
						'longitude': 12.57792893289,
						'is_vertical': True,
					},
				]
			}
		},
	},
	500: {
		'description': 'Internal Server Error',
		'content': {'application/json': {'example': {'detail': 'Internal Server Error'}}},
	},
}

