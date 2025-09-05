from .dependencies import Namespace


from .modules.user_data import UserDataResource
from .modules.providers import ProvidersResource
from .modules.metadata import MetadataResource
from .modules.analytics import AnalyticsResource


from .rest_side import Rest


class SDK(
	Rest, 
	UserDataResource, 
	ProvidersResource, 
	MetadataResource,
	AnalyticsResource
	):

	def __init__(self, api_key: str):

		self.meta = Namespace(
			domain='https://giftasset.pro',
			api_key=api_key,
			headers={
				"X-API-Key": api_key,
				"application": 'sdk'
			}
		)

		self.session = None