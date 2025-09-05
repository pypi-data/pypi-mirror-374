from ..dependencies import asyncio
from ..data import convert_params_to_url_args, remove_keys

class AnalyticsResource():

	async def get_gifts_collections_emission(
		self
	):
		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_gifts_collections_emission',
			headers = self.meta.headers
		)

	async def get_gifts_collections_marketcap(
		self
	):
		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_gifts_collections_marketcap',
			headers = self.meta.headers
		)

	async def get_gifts_price_list(
		self,
		models: bool = False
	):

		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_gifts_price_list?' + url_args,
			headers = self.meta.headers
		)

	async def get_gifts_price_list_history(
		self,
		collection_name: str
	):

		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_gifts_price_list_history?' + url_args,
			headers = self.meta.headers
		)

	async def get_gifts_update_stat(
		self
	):
		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_gifts_update_stat',
			headers = self.meta.headers
		)