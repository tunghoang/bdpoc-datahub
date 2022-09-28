import json

class Query:
    def __init__(self):
        self.query = ""

    def __call__(self, stage):
        self.query += stage
        return self

    def __repr__(self):
        return self.query

    def to_str(self):
        return self.query

    def from_bucket(self, bucket):
        return self(f'from(bucket: "{bucket}")')

    def range(self, time):
        return self(f'|> range(start: -{time})')

    def filter_measurement(self, measurement):
        return self(f'|> filter(fn: (r) => r._measurement == "{measurement}")')

    def filter_fields(self, fields):
        return self(f'|> filter(fn: (r) => contains(value: r._fields, set: {json.dumps(fields)}))')

    def keep_columns(self, *columns):
        return self(f'|> keep(columns: {json.dumps(columns)})')

    def interpolate(self):
        self.query = "import interpolate\n" + self.query
        return self(f'|> interpolate.linear(every: 1s)')

    def aggregate_window(self, create_empty):
        return self(f'|> aggregateWindow(every: 1s, fn: mean, createEmpty: {create_empty}')

    def yield_(self, name):
        return self(f'|> yield(name: "{name}")')

bucket = "datahub"
time = "10m"
device = "G1"
interpolated = True
missing_data = "NaN"
tags = ["123", "456"]
query = Query().from_bucket(bucket).range(time).filter_measurement(device).filter_fields(tags).keep_columns("_time", "_value", "_field")
if interpolated:
    query = query.interpolate()
query = query.aggregate_window("true" if missing_data == "NaN" else "false").yield_("mean").to_str()
print(query)