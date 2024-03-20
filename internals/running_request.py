from concurrent.futures import Future
import requests

import settings_parser
import psql_storage
from heapsort import HeapsortArray

class RunningRequest:
  def __init__(self, future: Future, wait_until: float,
      config_object: settings_parser.MonitoringTarget, heap_array: HeapsortArray):
    self.future = future
    self.wait_until = wait_until
    self.config_object = config_object
    self.is_handled = False
    
    # this class is coupled with heapsort algorithm
    # because in order to remove running request from
    # array, we need its index
    self.heap_index = -1
    self.heap_array = heap_array
  
  def __lt__(self, other: 'RunningRequest') -> bool:
    return self.wait_until < other.wait_until
  
  def set_index(self, i: int):
    self.heap_index = i

  def on_response(self, response: requests.models.Response) -> psql_storage.RequestEntity:
    print("on_response")
    self.is_reached = True
    self.status_code = response.status_code
    request_result = self.config_object.on_request_done(response)
    return psql_storage.RequestEntity(self.config_object._target, request_result.is_reached, request_result.status_code, request_result.regex_match)
  
  def on_timeout(self) -> psql_storage.RequestEntity:
    print("on_timeout")
    self.is_reached = False
    self.future.cancel()
    self.heap_array.pop()
    self.config_object.on_timeout()
    return psql_storage.RequestEntity(self.config_object._target, False)
  
  def get_db_entity(self) -> psql_storage.RequestEntity:
    return psql_storage.RequestEntity(self.config_object._target, False)