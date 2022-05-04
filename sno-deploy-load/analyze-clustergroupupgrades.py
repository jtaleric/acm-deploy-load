#!/usr/bin/env python3
#  Copyright 2022 Red Hat
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from datetime import datetime
import json
from utils.command import command
import logging
import numpy as np
import sys
import time


logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(levelname)s : %(threadName)s : %(message)s")
logger = logging.getLogger("analyze-clustergroupupgrades")
logging.Formatter.converter = time.gmtime


def main():
  start_time = time.time()
  logger.info("Analyze clustergroupupgrades")
  cgu_csv_file = "clustergroupupgrades.csv"

  oc_cmd = ["oc", "get", "clustergroupupgrades", "-n", "ztp-install", "-o", "json"]
  rc, output = command(oc_cmd, False, retries=3, no_log=True)
  if rc != 0:
    logger.error("analyze-clustergroupupgrades, oc get clusterdeployment rc: {}".format(rc))
    sys.exit(1)
  cd_data = json.loads(output)

  with open(cgu_csv_file, "w") as csv_file:
    csv_file.write("name,status,startedAt,completedAt,duration\n")

  cgu_upgradecompleted_values = []
  for item in cd_data["items"]:
    cgu_name = item["metadata"]["name"]
    cgu_status = "unknown"
    cgu_startedAt = item["status"]["status"]["startedAt"]
    cgu_completedAt = item["status"]["status"]["completedAt"]
    cgu_duration = 0
    for condition in item["status"]["conditions"]:
      if condition["type"] == "Ready":
        cgu_status = condition["reason"]
        break;

    if cgu_status == "UpgradeCompleted":
      start = datetime.strptime(cgu_startedAt, "%Y-%m-%dT%H:%M:%SZ")
      end = datetime.strptime(cgu_completedAt, "%Y-%m-%dT%H:%M:%SZ")
      cgu_duration = (end - start).total_seconds()
      cgu_upgradecompleted_values.append(cgu_duration)

    # logger.info("{},{},{},{},{}".format(cgu_name, cgu_status, cgu_startedAt, cgu_completedAt, cgu_duration))

    with open(cgu_csv_file, "a") as csv_file:
      csv_file.write("{},{},{},{},{}\n".format(cgu_name, cgu_status, cgu_startedAt, cgu_completedAt, cgu_duration))

  logger.info("Stats only on clustergroupupgrades CRs in UpgradeCompleted")
  logger.info("Count: {}".format(len(cgu_upgradecompleted_values)))
  logger.info("Min: {}".format(np.min(cgu_upgradecompleted_values)))
  logger.info("Average: {}".format(round(np.mean(cgu_upgradecompleted_values), 1)))
  logger.info("50 percentile: {}".format(round(np.percentile(cgu_upgradecompleted_values, 50), 1)))
  logger.info("95 percentile: {}".format(round(np.percentile(cgu_upgradecompleted_values, 95), 1)))
  logger.info("99 percentile: {}".format(round(np.percentile(cgu_upgradecompleted_values, 99), 1)))
  logger.info("Max: {}".format(np.max(cgu_upgradecompleted_values)))

  end_time = time.time()
  logger.info("Took {}s".format(round(end_time - start_time, 1)))


if __name__ == "__main__":
  sys.exit(main())
