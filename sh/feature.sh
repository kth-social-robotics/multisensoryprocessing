#!/bin/bash
open -a Terminal.app run_feature.sh

sleep 10

open -a Terminal.app run_nlp.sh

sleep 2

open -a Terminal.app run_asr.sh

sleep 2

open -a Terminal.app run_mic2.sh
