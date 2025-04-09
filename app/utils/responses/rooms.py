get_room_by_id_responses: dict[int | str, dict[str, object]] = {
	200: {
		'description': 'Successful Response',
		'content': {
			'application/json': {'example': {'id': '123', 'name': 'Room 1', 'capacity': 10}}
		},
	},
	400: {
		'description': 'Invalid Room ID',
		'content': {'application/json': {'example': {'detail': 'Invalid Room ID'}}},
	},
	404: {
		'description': 'Room not found',
		'content': {'application/json': {'example': {'detail': 'Room not found'}}},
	},
	500: {
		'description': 'Internal Server Error',
		'content': {'application/json': {'example': {'detail': 'Internal Server Error'}}},
	}
}

get_rooms_responses: dict[int | str, dict[str, object]] = {
	200: {
		'description': 'Successful Response',
		'content': {
			'application/json': {
				'example': [
					{'id': '123', 'name': 'Room 1', 'capacity': 10},
					{'id': '124', 'name': 'Room 2', 'capacity': 20},
				]
			}
		},
	},
	500: {
		'description': 'Internal Server Error',
		'content': {'application/json': {'example': {'detail': 'Internal Server Error'}}},
	}
}