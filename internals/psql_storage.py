import psycopg2
import time

import settings_parser


class RequestEntity:
  def __init__(self, url: str, is_reached: bool, status_code: int| None  = None, found_pattern: bool | None = None):
    self.url = url
    self.is_reached = is_reached
    self.status_code = status_code
    self.found_pattern = found_pattern

def convert_to_sql_type(value) -> str:
  if value is None:
    return "NULL"
  if value == True:
    return "true"
  if value == False:
    return "false"
  if isinstance(value, str):
    return "'" + value + "'"
  return str(value)
  
def get_insert_values(request_entity: RequestEntity):
  return "(" + ",".join(
    [convert_to_sql_type(request_entity.url), convert_to_sql_type(request_entity.is_reached), convert_to_sql_type(request_entity.status_code), convert_to_sql_type(request_entity.found_pattern)]
  ) + ")"

class SqlStore:
  def __init__(self, connection_string: str):
    self.connect = psycopg2.connect(connection_string)
    self.cursor = self.connect.cursor()
    self.collected_responses = []
    self.send_query_time = time.monotonic() + 1
    self.max_collected_responses = 20

  def upsert_target(self, target: settings_parser.MonitoringTarget):
      self.cursor.execute(f"INSERT INTO app_data.targets (url) VALUES ('{target._target}') ON CONFLICT DO NOTHING")
  
  # not used anymore
  #def insert_request_result(self, request: RequestEntity):
  #  self.cursor.execute(
  #    "INSERT INTO app_data.requests (url, is_reached, status_code, found_pattern) VALUES " + 
  #    get_insert_values(request))
  
  def send_collected_requests(self):
    if len(self.collected_responses) > 0:
      print("send collected requests")
      self.cursor.execute(
        "INSERT INTO app_data.requests (url, is_reached, status_code, found_pattern) VALUES " + 
        ', '.join([get_insert_values(r) for r in self.collected_responses]))
      self.collected_responses.clear()
      self.send_query_time = time.monotonic() + 1

  def collect_response(self, request):
    self.collected_responses.append(request)
    if len(self.collected_responses) > self.max_collected_responses:
      self.send_collected_requests()
  
  def should_send_data(self):
    return self.send_query_time > time.monotonic()


  def close(self):
    self.cursor.commit()
    self.cursor.close()
    self.connect.close()
