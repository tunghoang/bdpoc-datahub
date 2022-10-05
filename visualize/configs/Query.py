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
        return self(f'|> filter(fn: (r) => contains(value: r._field, set: {json.dumps(fields)}))')

    def keep_columns(self, *columns):
        return self(f'|> keep(columns: {json.dumps(columns)})')

    def interpolate(self):
        self.query = 'import "interpolate"\n' + self.query
        return self(f'|> interpolate.linear(every: 1s)')

    def aggregate_window(self, create_empty=False):
        return self(f'|> aggregateWindow(every: 1s, fn: mean, createEmpty: {"true" if create_empty else "false"})')

    def yield_(self, name):
        return self(f'|> yield(name: "{name}")')

    def pivot(self, row_key, column_key, value_column):
        return self(f'|> pivot(rowKey: ["{row_key}"], columnKey: ["{column_key}"], valueColumn: "{value_column}")')