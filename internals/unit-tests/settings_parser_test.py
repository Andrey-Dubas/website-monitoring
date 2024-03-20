import pytest
import json

import settings_parser as settings_parser

def test_extract_settings_double_target():
  test_data = [
    {
      "target": "A",
      "poll_period": "1s",
      "max_wait_time": "500ms"
    },
    {
      "target": "B",
      "poll_period": "1h",
      "max_wait_time": "2m"
    },
    {
      "target": "A",
      "poll_period": "1m",
      "max_wait_time": "1m"
    },
  ]

  with pytest.raises(ValueError) as ex:
    settings_parser.extract_settings(json.dumps(test_data))
  assert str(ex.value) == "target 'A' has multiple settings item"

def test_extract_settings__no_mandatory_attribute():
  test_data = [
    {
      "target": "A",
      "poll_period": "1s",
    },
  ]
  with pytest.raises(ValueError) as ex:
    settings_parser.extract_settings(json.dumps(test_data))

  assert str(ex.value) == f"failed parsing json: {test_data[0]}: no mandatory attribute max_wait_time"

def test_extract_settings_extra_attribute():
  test_data = [
    {
      "target": "A",
      "poll_period": "1s",
      "max_wait_time": "1m",
      "attr": '4'
    },
  ]
  with pytest.raises(ValueError) as ex:
    settings_parser.extract_settings(json.dumps(test_data))

  assert str(ex.value) == f"{test_data[0]} contains not supported attribute attr"

def test_convert_time_correct_time():
  assert settings_parser.convert_time("1s") == 1

def test_convert_time_without_unit():
  assert settings_parser.convert_time("1") == 1

def test_convert_time_with_space():
  assert settings_parser.convert_time("1 m") == 60

def test_convert_time_wrong_unit():
  with pytest.raises(ValueError) as ex:
    assert settings_parser.convert_time("1d")

  assert str(ex.value) == "1d contains wrong unit of time, options: '','ms','s','m','h'"
