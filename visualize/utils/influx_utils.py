from configs.constants import BUCKET, CHECK_BUCKET, ORG
from configs.influx_client import client
from configs.module_loader import *
from configs.Query import Query
from services.influx_services import get_check, get_database_by_table_mode

warnings.simplefilter("ignore", MissingPivotFunction)


def query_raw_data(time: int, device: str, tags: list = [], interpolated: bool = False, missing_data: str = "NaN", table_mode: str = "thin") -> DataFrame:
  if (not device) or (len(tags) == 0):
    return DataFrame()
  query = Query().from_bucket(BUCKET).range(time).filter_measurement(device).filter_fields(tags).keep_columns("_time", "_value", "_field")
  if interpolated:
    query = query.interpolate()
  query = query.aggregate_window(True if missing_data == "NaN" else False).to_str()
  # print(query)
  pivot_query = Query().from_bucket(BUCKET).range(time).filter_measurement(device).filter_fields(tags).keep_columns("_time", "_value", "_field").aggregate_window(True).pivot("_time", "_field", "_value").to_str()
  table = get_database_by_table_mode(table_mode, query if table_mode == "thin" else pivot_query)
  if "_time" in table:
    table["_time"] = table["_time"].dt.tz_convert(pytz.timezone("Asia/Ho_Chi_Minh"))
  return table


def query_check_data(time: int, device: str, tags: list = [], check_mode='none') -> DataFrame:
  if (not device) or (len(tags) == 0) or check_mode == 'none':
    return DataFrame()
  print("querying check data")
  query = Query().from_bucket(CHECK_BUCKET).range(time)
  if check_mode != 'all':
    query.filter_measurement(check_mode)
  query = query.filter_fields(tags).to_str()
  table = get_check(query)
  return table


def dataframe_to_dictionary(df, measurement):
  df["_time"] = to_datetime(df['_time'], errors='coerce').astype(np.int64)
  lines = [{"measurement": f"{measurement}", "tags": {"device": row["_measurement"]}, "fields": {row["_field"]: float(row["_value"])}, "time": row["_time"]} for _, row in df.iterrows() if row["_value"] != 0 and not math.isnan(row["_value"])]
  return lines
