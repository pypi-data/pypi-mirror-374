"""Driver for Slack"""

# General imports
import json

# Libs import
from slack_sdk import WebClient


# App imports
from .abstract import AlertAbstract


class Instance(AlertAbstract):
	"""Slack Implementation of Abstract class"""

	channel = "#alerts"
	client = None
	priority_emojis = {
		"P1": ":rotating_light:",  # Critical
		"P2": ":bangbang:",  # High
		"P3": ":warning:",  # Medium
		"P4": ":information_source:",  # Low
		"P5": ":speech_balloon:",  # Info
	}
	username = "AlertBot"
	token = ""

	def critical(self, msg, payload, channel=None):
		"""Send critical severity alert"""
		return self._send_alert(self._parse_payload(msg, payload, channel, "P1"))

	def high(self, msg, payload, channel=None):
		"""Send high severity alert"""
		return self._send_alert(self._parse_payload(msg, payload, channel, "P2"))

	def info(self, msg, payload, channel=None):
		"""Send very low severity alert"""
		return self._send_alert(self._parse_payload(msg, payload, channel, "P5"))

	def low(self, msg, payload, channel=None):
		"""Send low severity alert"""
		return self._send_alert(self._parse_payload(msg, payload, channel, "P4"))

	def medium(self, msg, payload, channel=None):
		"""Send medium severity alert"""
		return self._send_alert(self._parse_payload(msg, payload, channel, "P3"))

	def set_config(self, cfg):
		"""Set Slack webhook config"""
		self.channel = cfg.get("channel") or self.channel
		self.token = cfg.get("token")
		self.username = cfg.get("username") or self.username
		self.client = WebClient(token=self.token)

	def _parse_payload(self, msg, payload, channel=None, priority="P3"):
		"""Parse payload"""
		emoji = self.priority_emojis.get(priority, ":grey_question:")
		payload_str = json.dumps(payload or {}, indent=2)
		return {
			"channel": channel or self.channel,
			"text": f"{emoji} *{priority}* - {msg}\n```json\n{payload_str}\n```",
			"username": self.username,
		}

	def _send_alert(self, payload):
		"""Send alert"""
		return self.client.chat_postMessage(**payload)
