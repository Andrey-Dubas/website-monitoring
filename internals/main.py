import sys
import os
import time
import signal
from pathlib import Path

from requests_futures.sessions import FuturesSession

from heapsort import HeapsortArray
from running_request import RunningRequest
import psql_storage
import settings_parser

CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING', default = None)

def get_response_hook(request: RunningRequest, sql_executor: psql_storage.SqlStore):
  def response_hook(response, **kwargs):
    if not request.is_handled:
      request.is_handled = True
      print("handle response")
      request_entity = request.on_response(response)
      sql_executor.collect_response(request_entity)
  return response_hook

def poll_loop(monitoring_target_objects, heap_active_request_array, sql_executor):
  print("start poll loop")
  while True:
    if len(monitoring_target_objects) > 0 and monitoring_target_objects[0].next_poll_time < time.monotonic():
      next_target = monitoring_target_objects.pop()
      session = FuturesSession()
      url, wait_until_monotonic = next_target.request()
      monitoring_target_objects.push(next_target)
      future = session.get(url)
      running_request = RunningRequest(future, wait_until_monotonic, next_target, heap_active_request_array)
      session.hooks['response'] = get_response_hook(running_request, sql_executor)
      heap_active_request_array.push(running_request)

    while len(heap_active_request_array) > 0:
      if heap_active_request_array.array[0].wait_until < time.monotonic():
        request = heap_active_request_array[0]
        request_result = request.on_timeout()
        sql_executor.collect_response(request_result)
      else:
        break
    
    if sql_executor.should_send_data():
      sql_executor.send_collected_requests()

if __name__ == "__main__":
  if len(sys.argv) == 2:
    filepath = sys.argv[1]
  if not os.path.exists(filepath):
    print(f'{filepath} does not exist', file=sys.stderr)
    exit(1)
  if not os.path.isfile(filepath):
    print(f'{filepath} is not a file', file=sys.stderr)
    exit(1)
  print(f"starting the app, using {filepath} settings")

  json_plain_text = Path(filepath).read_text()
  json_dicts = settings_parser.extract_settings(json_plain_text)
  monitoring_target_objects = HeapsortArray(list(map(settings_parser.MonitoringTarget, json_dicts)), settings_parser.MonitoringTarget.__lt__)
  
  heap_active_request_array = HeapsortArray(
    [], 
    lambda a, b: a.wait_until < b.wait_until, 
    RunningRequest.set_index,
  )
  sql_executor = psql_storage.SqlStore(CONNECTION_STRING)

  for target in monitoring_target_objects:
    sql_executor.upsert_target(target)
  
  def handler(signum, _):
    print('signal handler called with signal', signum)
    sql_executor.close()
    exit(1)

  signal.signal(signal.SIGINT, handler)
  signal.signal(signal.SIGTERM, handler)

  poll_loop(monitoring_target_objects, heap_active_request_array, sql_executor)