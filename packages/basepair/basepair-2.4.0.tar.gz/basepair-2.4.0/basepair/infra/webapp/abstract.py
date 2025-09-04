"""Webapp API"""

# General imports
import json
import os

# Lib imports
import requests

# App imports
from basepair.helpers import eprint


class Abstract:
	"""Webapp abastract class"""

	def __init__(self, cfg):
		"""Constructor"""
		protocol = "https" if cfg.get("ssl", True) else "http"
		prefix = cfg.get("prefix")
		self.protocol = protocol
		self.host = cfg.get("host")
		self.endpoint = f"{protocol}://{self.host}{prefix}"
		self.payload = {"username": cfg.get("username"), "api_key": cfg.get("key")}
		self.headers = {"content-type": "application/json"}

	def delete(self, obj_id, verify=True):
		"""Delete resource"""
		try:
			response = requests.delete(
				f"{self.endpoint}{obj_id}",
				params=self.payload,
				timeout=5,
				verify=verify,
			)
			return self._parse_response(
				response,
				error_msgs=self._get_error_message(obj_id),
			)
		except requests.exceptions.RequestException as error:
			eprint(f"ERROR: {error}")
			return {"error": True, "msg": error}

	# pylint: disable=dangerous-default-value
	def get(
		self,
		obj_id,
		cache=False,
		params={},
		verify=True,
	):
		"""Get detail of an resource"""
		if not obj_id:
			return {"error": True, "msg": "Invalid or missing object id"}

		_cache = Abstract._get_from_cache(cache)
		if _cache:
			return _cache

		params.update(self.payload)
		try:
			response = requests.get(
				self.resource_url(obj_id),
				params=params,
				timeout=5,
				verify=verify,
			)
			parsed = self._parse_response(
				response,
				error_msgs=self._get_error_message(obj_id),
			)

			# save in cache if required
			Abstract._save_cache(cache, parsed)
			return parsed
		except requests.exceptions.RequestException as error:
			eprint(f"ERROR: {error}")
			return {"error": True, "msg": error}

	# pylint: disable=dangerous-default-value
	def list(
		self,
		cache=False,
		params={"limit": 100},
		verify=True,
	):
		"""Get a list of items"""
		_cache = Abstract._get_from_cache(cache)
		if _cache:
			return _cache

		params.update(self.payload)
		try:
			response = requests.get(
				self.endpoint.rstrip("/"),
				params=params,
				timeout=5,
				verify=verify,
			)
			parsed = self._parse_response(response)

			# save in cache if required
			Abstract._save_cache(cache, parsed)
			return parsed
		except requests.exceptions.RequestException as error:
			eprint(f"ERROR: {error}")
			return {"error": True, "msg": error}

	def list_all(self, filters={}):  # pylint: disable=dangerous-default-value
		"""Get a list of all items"""
		item_list = []
		limit = filters.get("limit", 100)  # default limit = 100
		offset = 0
		total_count = 1
		while len(item_list) < total_count:
			params = {"limit": limit, "offset": offset}
			params.update(filters)
			# response = self.list({**filters, 'limit': limit, 'offset': offset}) #TODO: Uncomment when everything moved to py3
			response = self.list(params=params)
			if response.get("error"):
				return {"error": True, "msg": response.get("msg")}
			total_count = response.get("meta", {}).get("total_count")
			item_list += response.get("objects")
			offset += limit
		return item_list

	def list_all_full(self, filters={}):
		"""Get all items but return full response format like list()"""
		item_list = []
		limit = filters.get("limit", 100)
		offset = 0
		total_count = 1
		while len(item_list) < total_count:
			params = {"limit": limit, "offset": offset}
			params.update(filters)
			# Reuse the list() method here
			response = self.list(params=params)
			if response.get("error"):
				return {"error": True, "msg": response.get("msg")}
			total_count = response.get("meta", {}).get("total_count", 0)
			item_list += response.get("objects", [])
			offset += limit

		meta = response.get("meta", {})
		meta["total_count"] = total_count
		meta["returned_count"] = len(item_list)
		return {"meta": meta, "objects": item_list}

	def resource_uri(self, obj_id):
		"""Generate resource uri from obj id"""
		return f"{self.pathname}{obj_id}"

	def resource_url(self, obj_id):
		"""Generate resource uri from obj id"""
		return f"{self.endpoint}{obj_id}"

	# pylint: disable=dangerous-default-value
	def save(
		self,
		obj_id=None,
		params={},
		payload={},
		verify=True,
	):
		"""Save or update resource"""
		params.update(self.payload)
		try:
			response = getattr(requests, "put" if obj_id else "post")(
				self.resource_url(obj_id) if obj_id else self.endpoint,
				data=json.dumps(payload),
				headers=self.headers,
				params=params,
				timeout=5,
				verify=verify,
			)
			return self._parse_response(
				response,
				error_msgs=self._get_error_message(obj_id),
			)
		except requests.exceptions.RequestException as error:
			eprint(f"ERROR: {error}")
			return {"error": True, "msg": error}

	@property
	def pathname(self):
		"""Get pathname"""
		return self.endpoint.replace(f"{self.protocol}://", "").replace(self.host, "")

	@staticmethod
	def _get_from_cache(cache):
		"""Helper to get data from cache"""
		if cache:
			filename = os.path.expanduser(cache)
			if os.path.exists(filename) and os.path.getsize(filename):
				with open(filename, "r", encoding="utf-8") as file:
					return json.loads(file.read().strip())
		return None

	@classmethod
	def _get_error_message(cls, obj_id):
		"""General response parser with obj id"""
		return {
			401: f"You don't have access to resource with id {obj_id}."
			if obj_id
			else "You don't have access to this resource.",
			404: f"Resource with id {obj_id} not found."
			if obj_id
			else "Resource not found.",
			500: "Error retrieving data from API!",
		}

	@classmethod
	def _parse_response(cls, response, error_msgs=None):
		"""General response parser"""
		error_msgs = error_msgs or {
			401: "You don't have access to this resource.",
			404: "Resource not found.",
			500: "Error retrieving data from API!",
		}
		if response.status_code in error_msgs:
			eprint(f"ERROR: {error_msgs[response.status_code]}")
			return {"error": True, "msg": error_msgs[response.status_code]}

		if response.status_code == 204:  # for delete response
			return {"error": False}

		try:
			response = response.json()
			error = isinstance(response, dict) and response.get("error")
			if error:
				if isinstance(error, dict):
					response = error
					msg = response.get("error_msgs")
					if msg:
						eprint(f"ERROR: {msg}")

					msg = response.get("warning_msgs")
					if msg:
						eprint(f"WARNING: {msg}")
				else:
					eprint(f"ERROR: {error}")

			return response
		except json.decoder.JSONDecodeError as error:
			msg = f"ERROR: Not able to parse response: {error}."
			eprint(msg)
			return {"error": True, "msg": msg}

	@staticmethod
	def _save_cache(cache, content):
		"""Helper to save the content in the cache"""
		if cache and content and not content.get("error"):
			filename = os.path.expanduser(cache)
			directory = os.path.dirname(filename)
			if not os.path.exists(directory):
				os.makedirs(directory)
			with open(filename, "w", encoding="utf-8") as handle:
				handle.write(json.dumps(content, indent=2))
