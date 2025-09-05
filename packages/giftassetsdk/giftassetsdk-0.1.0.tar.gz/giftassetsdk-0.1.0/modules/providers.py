from ..dependencies import asyncio
from ..data import convert_params_to_url_args, remove_keys

class ProvidersResource():

	async def get_attribute_volumes(
		self
	):
		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_attribute_volumes',
			headers = self.meta.headers
		)

	async def get_collection_offers(
		self, 
		collection_name: str
	):
		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_post(
			url = self.meta.domain + '/api/v1/gifts/get_collection_offers',
			headers = self.meta.headers,
			data=params
		)

	async def get_custom_collections_volumes(
		self,
		maxtime: int = 3600
	):

		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_custom_collections_volumes?' + url_args,
			headers = self.meta.headers
		)

	async def get_providers_fee(
		self
	):

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_providers_fee',
			headers = self.meta.headers
		)

	async def get_providers_sales_history(
		self,
		provider_name: str,
		limit: int,
		offset: int
	):

		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_providers_sales_history?' + url_args,
			headers = self.meta.headers
		)

	async def get_providers_volumes(
		self
	):

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_providers_volumes',
			headers = self.meta.headers
		)

	async def get_top_best_deals(
		self
	):

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_top_best_deals',
			headers = self.meta.headers
		)

	async def get_unique_deals(
		self,
		limit: int,
		offset: int,
		gift_min_price: int,
		collection_name: str = ''
	):

		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_unique_deals?' + url_args,
			headers = self.meta.headers
		)