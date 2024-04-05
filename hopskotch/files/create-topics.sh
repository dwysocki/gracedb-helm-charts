#!/bin/bash

namespace=$1
servername=$2

echo $namespace
echo $servername

while read t; do
  topic="$namespace.$t"
  echo $topic
  success=10
  while [ $success -gt 0 ]; do
    bash -c "echo dummy | kcat -P -b $servername:9092 -t $topic"
    success=$?
    echo $success
  done
done < /tmp/topics.txt

