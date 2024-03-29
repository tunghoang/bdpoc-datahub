import sys
import time
import warnings
import traceback
from os import path
from threading import Thread
from visualize.configs.logger import check_logger
from dateutil import parser as dparser
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import schedule
from influxdb_client.client.warnings import MissingPivotFunction

sys.path.append(path.join(path.dirname(__file__), "visualize"))
#from configs.query import Query

from visualize.views.container import tagSpecFile
from visualize.configs.constants import (BUCKET, CHECK_PERIOD, MONITORING_BUCKET, ORG, TAG_FILES)
from visualize.configs.influx_client import query_api, write_api
from visualize.configs.logger import check_logger

from visualize.checks.nan_check import do_nan_check
from visualize.checks.overange_check import do_overange_check
from visualize.checks.roc_check import do_roc_check

from visualize.services.check_services import (do_deviation_check, do_irv_check)
from visualize.utils.tag_utils import load_tag_config, load_tag_specs
from influx import Influx

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--machine")
args = parser.parse_args()
#__tagFileName = "assets/files/tags.yaml" if args.machine == "MP" else 'assets/files/lip-tags.yaml'
__tagFileName = TAG_FILES[args.machine.lower()]


control_logic_checks, deviation_checks, devices = load_tag_config(__tagFileName)

tags = [tag["tag_number"] for d in devices for tag in d["tags"]]
warnings.simplefilter("ignore", MissingPivotFunction)

def process(table, interpolated_table):
  #do_nan_check(table, tags)
  #do_overange_check(interpolated_table, tags, devices)
  #do_irv_check(interpolated_table, devices, tags)
  do_roc_check(interpolated_table)
  do_deviation_check(interpolated_table, deviation_checks, devices)
  #do_frozen_check(interpolated_table, devices)
def processParallel(table, interpolated_table):
  tagDict = load_tag_specs(tagSpecFile(args.machine.lower()))
  #if args.machine != "LIP":
    #t1 = Thread(target=do_nan_check, args=(table, tags))
#  t2 = Thread(target=do_overange_check, args=(interpolated_table, tags, devices))
  #t3 = Thread(target=do_irv_check, args=(interpolated_table, devices, tags))
  t4 = Thread(target=do_deviation_check, args=(interpolated_table, deviation_checks, devices, tagDict))
#  t5 = Thread(target=do_roc_check, args=(interpolated_table, ))
  #t6 = Thread(target=do_frozen_check, args=(interpolated_table, devices))

  #if args.machine != "LIP":
    #t1.start()

#  t2.start()
  #t3.start()
  t4.start()
#  t5.start()
  #t6.start()

  #if args.machine != "LIP":
    #t1.join()
#  t2.join()
  #t3.join()
  #if args.machine in ('MP', ):
  t4.join()
#  t5.join()
  #t6.join()
  write_api.write(MONITORING_BUCKET, ORG, {"measurement": "check_harvest", "fields": {"rate": 1.0}})
  check_logger.info("All Done")
  
def job():
  check_logger.info("Querying ...")
  
  instance = Influx().from_now(2 * CHECK_PERIOD).addFields(tags)
  table = instance.setInterpolation(False).setRate('1s').asPivotDataFrame()
  interpolated_table = instance.setInterpolation(True).setRate('1s').asPivotDataFrame()
  check_logger.info("Query done")
  processParallel(table, interpolated_table)
  
def job1(startTime, stopTime):
  instance = Influx().setStart(startTime).setStop(stopTime).addFields(tags)
  table = instance.setInterpolation(False).asPivotDataFrame()
  interpolated_table = instance.setInterpolation(True).setRate('1s').asPivotDataFrame()
  
  check_logger.info("Query done")
  processParallel(table, interpolated_table)

job1(dparser.isoparse("2023-09-26T15:10:00+07:00"), dparser.isoparse("2023-09-26T15:20:00+07:00"))
