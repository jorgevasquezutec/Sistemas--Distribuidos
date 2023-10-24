#!/bin/bash

# Function to run JMeter tests
run_jmeter_test() {
  local num_requests=$1
  local jmx_file=$2

  echo "Running JMeter tests with $num_requests requests"

  docker run -v "$(pwd)/jmeter:/jmeter" -v "$(pwd)/results:/results" \
    --name jmeter -it --rm --network host \
    -e numofreq=$num_requests \
    justb4/jmeter -n -t /jmeter/$jmx_file -l /results/test_${num_requests}.jtl

  echo "JMeter tests with $num_requests requests completed."
}


run_jmeter_test 2 test.jmx
