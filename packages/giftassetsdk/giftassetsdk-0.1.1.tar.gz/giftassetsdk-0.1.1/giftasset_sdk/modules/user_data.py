from ..dependencies import asyncio
from ..data import convert_params_to_url_args, remove_keys

class UserDataResource():

	async def get_all_collections_by_user(
		self, 
		username: str, 
		include: list[str], 
		exclude: list[str], 
		limit: int = 10, 
		offset: int = 0
	):
		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_post(
			url = self.meta.domain + '/api/v1/gifts/get_all_collections_by_user?' + list_of_args[0],
			headers = self.meta.headers,
			data=remove_keys(params, 'username')
		)

	async def get_gift_by_name(
		self, 
		name: str
	):
		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_gift_by_name?' + url_args,
			headers = self.meta.headers
		)

	async def get_gift_by_user(
		self, 
		username: str,
		limit: int = 5,
		offset: int = 0
	):
		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_gift_by_user?' + url_args,
			headers = self.meta.headers
		)

	async def get_user_profile_price(
		self, 
		username: str,
		limit: int = 5,
		offset: int = 0
	):
		params = locals()
		del params['self']

		url_args, list_of_args = convert_params_to_url_args(params=params)

		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_user_profile_price?' + url_args,
			headers = self.meta.headers
		)
