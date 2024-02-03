#!/usr/bin/env bash

MODULE="formulautils.file_switch"
SALT_RUN="salt-call --local --module-dirs=. --out=json ${MODULE} "

[ -d tmp ] || mkdir tmp
echo "[test.yaml,test] tlp"
${SALT_RUN} "[test.yaml,test]" tlp | tee tmp/run_0.json
echo "test.yaml tlp use_subpath=true"
${SALT_RUN} test.yaml tlp use_subpath=true | tee tmp/run_1.json
echo "[test.yaml,test] tlp/nested/more"
${SALT_RUN} "[test.yaml,test]" tlp/nested/more | tee tmp/run_2.json
echo "[test.yaml,test] tlp/nested/more use_subpath=true"
${SALT_RUN} "[test.yaml,test]" tlp/nested/more use_subpath=true | \
    tee tmp/run_3.json
