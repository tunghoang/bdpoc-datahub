import pandas as pd
from configs.constants import (BUCKET, CHECK_BUCKET, CHECK_MONITORING_PERIOD, CHECK_PERIOD, CHECKS_LIST, MONITORING_AGG_WINDOW, MONITORING_BUCKET, MONITORING_FIELD, MONITORING_MEASUREMENT, MONITORING_PERIOD, ORG, PIVOT, SECOND)
from configs.influx_client import query_api
from configs.module_loader import *
from configs.Query import Query
from services.influx_services import (get_check, get_check_harvest_rate, get_database, get_tag_harvest_rate)
from utils.tag_utils import load_tag_specs

warnings.simplefilter("ignore", MissingPivotFunction)


def query_raw_data(time: int, device: str, tags: list = [], interpolated: bool = False, missing_data: str = "NaN") -> DataFrame:
  if len(tags) == 0:
    return DataFrame()
  query = Query().from_bucket(BUCKET).range(time)
  if device:
    query = query.filter_measurement(device)
  query = query.filter_fields(tags).keep_columns("_time", "_value", "_field").aggregate_window(True if missing_data == "NaN" else False).to_str()
  table = get_database(query)
  if interpolated:
    test = table["_time"]
    table = table.drop(columns=["_time", "_start", "_stop"]).interpolate(method='linear', limit_direction='both', axis=0).assign(_time=test)
  return table


def query_irv_tags(time: int) -> DataFrame:
  tagDict = load_tag_specs()

  irv_fields = list(filter(lambda x: tagDict[x]["high"] is not None, tagDict.keys()))
  query = Query().from_bucket(BUCKET).range(time).filter_fields(irv_fields).keep_columns("_time", "_measurement", "_value", "_field").aggregate_window(False).to_str()

  results = query_api.query_data_frame(query, org=ORG)
  if type(results) == list:
    return pd.concat(results)
  return results


def query_check_data(time: int, device: str, tags: list = [], check_mode='none') -> DataFrame:
  if (not device) or (len(tags) == 0) or check_mode == 'none':
    return DataFrame()
  query = Query().from_bucket(CHECK_BUCKET).range(time)
  if check_mode != 'all':
    query.filter_measurement(check_mode)
  query = query.filter_fields(tags).to_str()
  table = get_check(query)
  if table.empty:
    assert Exception("No data found")
  return table


def query_check_all(time: int) -> DataFrame:
  print('Query_check_all')
  query = Query().from_bucket(CHECK_BUCKET).range(time).to_str()
  print(query)
  table = get_check(query)
  return table


def dataframe_to_dictionary(df, measurement):
  df["_time"] = to_datetime(df['_time'], errors='coerce').astype(np.int64)
  lines = [{"measurement": f"{measurement}", "tags": {"device": row["_measurement"]}, "fields": {row["_field"]: float(row["_value"])}, "time": row["_time"]} for _, row in df.iterrows() if row["_value"] != 0 and not math.isnan(row["_value"])]
  return lines


def collector_status() -> float:
  query = Query().from_bucket(MONITORING_BUCKET).range(MONITORING_PERIOD).filter_measurement(MONITORING_MEASUREMENT).filter_fields([MONITORING_FIELD]).aggregate_window(False, MONITORING_AGG_WINDOW).to_str()
  result = get_tag_harvest_rate(query)
  return "{:.2f}".format(result)


def check_status() -> float:
  query = Query().from_bucket(MONITORING_BUCKET).range(CHECK_MONITORING_PERIOD).filter_measurement("check_harvest").aggregate_window(True, MONITORING_AGG_WINDOW).fill().to_str()
  result = get_check_harvest_rate(query) * (len(CHECKS_LIST.keys()) - 1) * SECOND * (CHECK_PERIOD * 2)
  return "{:.2f}".format(result)
