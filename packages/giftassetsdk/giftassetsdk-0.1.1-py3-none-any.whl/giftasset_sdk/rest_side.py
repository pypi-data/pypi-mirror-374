from .dependencies import aiohttp, Namespace, json


class Rest():


	async def rest_get(self, url: str, headers: dict):

		if self.session == None:
			self.session = aiohttp.ClientSession()

		async with self.session.get(url=url, headers=headers) as response:
			return await response.json()


	async def rest_post(self, url: str, headers: dict, data: dict):

		if self.session == None:
			self.session = aiohttp.ClientSession()

		async with self.session.post(url=url, headers=headers, json=data) as response:
			return await response.json()