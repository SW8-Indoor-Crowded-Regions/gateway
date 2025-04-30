import requests
from collections import Counter

total_techniques = 0


def fetch_all_artworks():
	"""Fetch all artworks from the SMK API."""
	base_url = 'https://api.smk.dk/api/v1/art/search'
	page = 1
	page_size = 100
	all_artworks = []
	data = {}

	while True:
		response = requests.get(
			base_url,
			params={
				'keys': '*',
				'offset': (page - 1) * 100,
				'rows': page_size,
				'filters': '[on_display:true]',
				'facets': ['creator', 'materials'],
			},
		)
		if response.status_code != 200:
			print(f'Failed to fetch data: {response.status_code}')
			print(response.url)
			break
		data = response.json()
		artworks = data.get('items', [])
		if not artworks:
			break

		all_artworks.extend(artworks)
		page += 1

	return all_artworks, data.get('facets', {})

def get_facet_count(facets: dict, facet_name: str) -> list[dict]:
	"""Get the creators of the artworks and their counts."""
	facets = facets.get(facet_name, [])
	facet_list: list[dict] = []
	for i in range(0, len(facets), 2):
		name = facets[i]
		count = facets[i + 1]
		facet_list.append({'name': name, 'count': count})
		
	return facet_list


def main():
	print('Fetching all artworks from SMK API...')
	artworks, facets = fetch_all_artworks()
	print(f'Fetched {len(artworks)} artworks.')
 
	# Count the occurrences of each facet
	for facet in facets:
		objs = get_facet_count(facets, facet)
		print(f'{str(facet).capitalize()}:')
		for obj in objs:
			print(f"	{str(obj['name']).ljust(33).capitalize()} {str(obj['count']).rjust(3)}")

	



if __name__ == '__main__':
	main()
