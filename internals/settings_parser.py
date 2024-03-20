import json
import re
import time
import requests

POLL_PERIOD_ATTRRIBUTE = "poll_period"
MAX_WAIT_ATTRRIBUTE = "max_wait_time"
TARGET_ATTRIBUTE = "target"
REGEX_EXPRESSION_ATTRIBUTE = "expected_regex"

class RequestResult:
  def __init__(self, is_reached: bool, status_code: int | None = None, regex_match: bool | None = None):
    self.is_reached = is_reached
    self.status_code = status_code
    self.regex_match = regex_match


class MonitoringTarget:
  """
    class for storing target configuration and statistics
    for a target website.
  """
  def __init__(self, attributes: dict):
    self.poll_period = attributes[POLL_PERIOD_ATTRRIBUTE]
    self.max_wait = attributes[MAX_WAIT_ATTRRIBUTE]
    self._target = attributes[TARGET_ATTRIBUTE]
    if '://' not in self._target:
      self._target = "https://" + self._target # default schema if absent
    self.regex = None
    if REGEX_EXPRESSION_ATTRIBUTE in attributes:
      self.regex = re.compile(attributes[REGEX_EXPRESSION_ATTRIBUTE])
    self.next_poll_time = time.monotonic()
    self.sequential_fail_times = 0
    self.active_connection_number = 0

  def request(self)-> str:
    self.active_connection_number += 1
    self.next_poll_time = time.monotonic() + self.poll_period
    return self._target, time.monotonic() + self.max_wait

  def on_index_change(self, current_index: int):
    self.self_index = current_index

  def active_connection_inc(self):
    self.active_connection_number += 1

  def on_request_done(self, response: requests.models.Response) -> RequestResult:
    self.sequential_fail_times = 0
    self.active_connection_number -= 1
    pattern_match = None
    if self.regex is not None:
      pattern_match = re.match(self.regex, response.text) is not None
    return RequestResult(True, response.status_code, pattern_match)
  
  def on_timeout(self) -> RequestResult:
    self.sequential_fail_times += 1
    self.active_connection_number -= 1
    return RequestResult(False)
  
  def __lt__(self, other)-> bool:
    return self.next_poll_time < other.next_poll_time
  
  def update_next_poll_time(self):
    self.next_poll_time = time.monotonic() + self.poll_period/1000

def verify_json_object(json_object: dict):
  required_attributes = [POLL_PERIOD_ATTRRIBUTE, MAX_WAIT_ATTRRIBUTE, TARGET_ATTRIBUTE]
  optional_attributes = [REGEX_EXPRESSION_ATTRIBUTE]
  for attribute in required_attributes:
    if attribute not in json_object:
      raise ValueError(f"failed parsing json: {json_object}: no mandatory attribute {attribute}")
  
  for json_attribute_name in json_object.keys():
    if json_attribute_name not in required_attributes + optional_attributes:
      raise ValueError(f"{json_object} contains not supported attribute {json_attribute_name}")


def extract_settings(data: bytes) -> dict:
  json_data = json.loads(data)
  defined_targets = set()
  for i, _ in enumerate(json_data):
    verify_json_object(json_data[i])
    if json_data[i][TARGET_ATTRIBUTE] in defined_targets:
      raise ValueError(f"target '{json_data[i][TARGET_ATTRIBUTE]}' has multiple settings item")
    defined_targets.add(json_data[i][TARGET_ATTRIBUTE])

    json_data[i][POLL_PERIOD_ATTRRIBUTE] = convert_time(json_data[i][POLL_PERIOD_ATTRRIBUTE])
    json_data[i][MAX_WAIT_ATTRRIBUTE] = convert_time(json_data[i][MAX_WAIT_ATTRRIBUTE])
  return json_data

def convert_time(s: str) -> int:
  s = s.strip(" ")
  number = -1
  number_ends_at = -1
  if s.isnumeric():
    return int(s)

  for i, ch in enumerate(s):
    if ch.isalpha() or ch == ' ':
      number = int(s[:i])
      number_ends_at = i
      break
  duration_unit = ""
  if number_ends_at == -1:
    raise ValueError(f"{s} does not contain a number")

  for i, ch in enumerate(s[number_ends_at:]):
    if ch != ' ':
      duration_unit = s[number_ends_at+i:]
      break

  multiplier_map = {"": 0.001, "ms": 0.001, "s": 1, "m": 60, 'h': 3600}
  if duration_unit not in multiplier_map:
    available_units_str = ','.join(map(lambda unit: "'" +unit+ "'", multiplier_map.keys()))
    raise ValueError(f"{s} contains wrong unit of time, options: {available_units_str}")
  
  return number * multiplier_map[duration_unit]
