get_filters_responses: dict[int | str, dict[str, object]] = {
	200: {
		'description': 'Successful Response',
		'content': {
			'application/json': {
				'example': [
					{
						'type': 'creator',
						'filters': [
							{
								'key': 'John Doe',
								'count': 10,
							},
							{
								'key': 'Jane Smith',
								'count': 5,
							},
						],
					},
					{
						'type': 'materials',
						'filters': [
							{
								'key': 'Lærred',
								'count': 8,
							},
							{
								'key': 'Marmor',
								'count': 3,
							},
						],
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


filter_to_rooms_responses: dict[int | str, dict[str, object]] = {
	200: {
		'description': 'Successful Response',
		'content': {
			'application/json': {
				'example': [
					'room1',
					'room2',
					'room3'
				]
			}
		},
	},
	500: {
		'description': 'Internal Server Error',
		'content': {'application/json': {'example': {'detail': 'Internal Server Error'}}},
	},
}