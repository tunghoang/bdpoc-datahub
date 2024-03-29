import sys
import time
import traceback
from datetime import datetime, timedelta
from os import path

import dateutil.parser as parser
import schedule

sys.path.append(path.join(path.dirname(__file__), "visualize"))
from configs.query import Query

from check_mp_speed_common import process
from visualize.configs.constants import (BUCKET, MP_SPEED_CHECK_PERIOD, ORG, SPEED_TAG)


def job():
  print("Querying ...")
  query = Query().from_bucket(BUCKET).range(f"{2 * MP_SPEED_CHECK_PERIOD}m").filter_fields([SPEED_TAG]).keep_columns("_time", "_value", "_field").aggregate_window(False, "10s").pivot("_time", "_field", "_value").duplicate(SPEED_TAG, 'derivative').derivative(non_negative=False,
                                                                                                                                                                                                                                                                  unit="1s",
                                                                                                                                                                                                                                                                  columns=["derivative"]).to_str()
  print(query)
  process(query)


def job1(startTime, stopTime):
  query = Query().from_bucket(BUCKET).range1(startTime, stopTime).filter_fields([SPEED_TAG]).keep_columns("_time", "_value", "_field").aggregate_window(False, "10s").pivot("_time", "_field", "_value").duplicate(SPEED_TAG, 'derivative').derivative(non_negative=False,
                                                                                                                                                                                                                                                       unit="1s",
                                                                                                                                                                                                                                                       columns=["derivative"]).to_str()
  print(startTime, " ----- ", stopTime)
  process(query)


if len(sys.argv) > 1:
  ## Catching up from argv[1]
  startTime = sys.argv[1]
  print(startTime)
  try:
    startTime = parser.isoparse(startTime)
    while startTime.timestamp() < datetime.now().timestamp():
      stopTime = startTime + timedelta(minutes=18 * MP_SPEED_CHECK_PERIOD)
      job1(startTime.isoformat(), stopTime.isoformat())
      startTime = stopTime
      time.sleep(0.5)
  except:
    traceback.print_exc()
    print("Wrong datetime format")
    exit(1)

schedule.every(MP_SPEED_CHECK_PERIOD).minutes.do(job)
while True:
  schedule.run_pending()
  time.sleep(1)
#job()
