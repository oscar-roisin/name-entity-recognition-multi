#!/bin/bash

if [ $# -ne 2 ]; then
  echo 1>&2 "Usage: inputFile outputFile"
  exit 3
fi

java -jar ../TAGGERS/stagger/stagger.jar -modelfile models/swedish.bin -tag "$1"
