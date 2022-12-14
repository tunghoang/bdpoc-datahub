from configs.checks import (deviation_check, frozen_check, irv_check,
                            nan_check, overange_check, roc_check)
from configs.constants import CHECK_BUCKET, ORG
from configs.influx_client import write_api
from configs.logger import check_logger
from utils.check_utils import check_gen


def do_roc_check(table, devices):
  roc_checks = roc_check(table, devices)
  for point in check_gen("roc_check", roc_checks):
    write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("roc_checking 1 point")
  check_logger.info("roc_checking done")


def do_deviation_check(table, deviation_checks_detail, devices):
  deviation_checks = deviation_check(table, deviation_checks_detail, devices)
  for point in check_gen("deviation_check", deviation_checks):
    write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("deviation_checking 1 point")
  check_logger.info("deviation_checking done")


def do_irv_check(table, devices, tags):
  irv_checks = irv_check(table, devices, tags)
  for point in check_gen("irv_check", irv_checks):
    write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("irv_checking 1 point")
  check_logger.info("irv_checking done")


def do_overange_check(table, tags, devices):
  overange_checks = overange_check(table, devices, tags)
  for point in check_gen("overange_check", overange_checks):
    write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("overange_checking 1 point")
  check_logger.info("overange_checking done")


def do_nan_check(table, tags):
  nan_checks = nan_check(table, tags)
  for point in check_gen("nan_check", nan_checks):
    write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("nan_checking 1 point")
  check_logger.info("nan_checking done")


def do_frozen_check(table, devices):
  frozen_checks = frozen_check(table, devices)
  for point in check_gen("frozen_check", frozen_checks):
    write_api.write(bucket=CHECK_BUCKET, record=point, org=ORG)
    check_logger.info("frozen_checking 1 point")
  check_logger.info("frozen_checking done")
