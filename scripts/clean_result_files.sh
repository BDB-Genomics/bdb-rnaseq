#!/bin/bash

for dir in results/*; do
   rm -rf "${dir}/*"
done
