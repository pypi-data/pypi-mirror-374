from ..dependencies import asyncio
from ..data import convert_params_to_url_args, remove_keys

class MetadataResource():

	async def get_attributes_metadata(
		self
	):
		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_attributes_metadata',
			headers = self.meta.headers
		)

	async def get_collections_metadata(
		self
	):
		return await self.rest_get(
			url = self.meta.domain + '/api/v1/gifts/get_collections_metadata',
			headers = self.meta.headers
		)