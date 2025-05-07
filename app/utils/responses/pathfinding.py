multipoint_path_response: dict[int | str, dict[str, object]] = {
	200: {
		'description': 'Fastest path found successfully',
		'content': {
			'application/json': {
				'example': {
					'path': [
						{
							'id': 'id123',
							'latitude': 55.6761,
							'longitude': 12.5683,
						},
						{
							'id': 'id456',
							'latitude': 55.6762,
							'longitude': 12.5684,
						},
						{
							'id': 'id789',
							'latitude': 55.6763,
							'longitude': 12.5685,
						}
					],
					'distance': 30,
				}
			}
		},
	},
	
}
