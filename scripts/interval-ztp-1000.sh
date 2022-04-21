#!/usr/bin/env bash
set -e
set -o pipefail

iteration=1
interval_period=7200

log_file="iz-1000-$(date -u +%Y%m%d-%H%M%S).log"
acm_ver=$(cat /root/rhacm-deploy/deploy/snapshot.ver)
test_ver="ZTP Scale Run ${iteration}"
hub_ocp=$(oc version -o json | jq -r '.openshiftVersion')
sno_ocp=$(grep "imageSetRef:" /root/hv-sno/manifests/sno00001/manifest.yml -A 1 | grep "name" | awk '{print $NF}' | sed 's/openshift-//')

time ./sno-deploy-load/sno-deploy-load.py --acm-version "${acm_ver}" --test-version "${test_ver}" --hub-version "${hub_ocp}" --sno-version "${sno_ocp}" -e 1000 -w -i 60 -t int-ztp-100-100b-${interval_period}i-${iteration} interval -b 100 -i ${interval_period} ztp 2>&1 | tee ${log_file}

results_dir=$(grep "Results data captured in:" $log_file | awk '{print $NF}')

time ./sno-deploy-load/sno-deploy-graph.py --acm-version "${acm_ver}" --test-version "${test_ver}" --hub-version "${hub_ocp}" --sno-version "${sno_ocp}" ${results_dir}

mv ${log_file} ${results_dir}