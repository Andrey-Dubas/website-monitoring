from flask import Flask
import time

app = Flask(__name__)


@app.route('/200/<content>')
def get_200_with_content(content):
  return content, 200

@app.route('/unavailable/for/<time_in_seconds>')
def wait_for(time_in_seconds):
  time.sleep(time_in_seconds)
  return "", 200

@app.route('/with_status_code/<status_code>/with_content/<content>')
def get_with_status_and_content(content, status_code):
  return content, status_code

request_counter = 0
@app.route('/unavailable_every_5th_request/<wait_time_in_secs>')
def get_with_status_and_content(wait_time_in_secs):
  global request_counter
  request_counter += 1
  if request_counter % 5 == 0:
    time.sleep(wait_time_in_secs)
  return "", 200


if __name__ == "__main__":
    app.run()