#! /bin/bash

set -e -o pipefail
set -x

python bin/simulate.py --nreps 100 -o simulated-data/target.unconstrained --debug -F archipelago -H host-data/H001.reps1.histories.json unconstrained
python bin/simulate.py --nreps 100 -o simulated-data/target.constrained --debug -F archipelago -H host-data/H001.reps1.histories.json constrained
python bin/simulate.py --nreps 100 -o simulated-data/training.unconstrained --debug -F archipelago -H host-data/H001.reps1.histories.json unconstrained
python bin/simulate.py --nreps 100 -o simulated-data/training.constrained --debug -F archipelago -H host-data/01-simulated-host-histories/H001.reps1.histories.json constrained
archipelago-classify.py -o results.performance.unconstrained.csv --describe results.unconstrained.txt --opt 0 --true-model unconstrained simulated-data/target.unconstrained.summary-stats.csv simulated-data/training.unconstrained.summary-stats.csv simulated-data/training.constrained.summary-stats.csv
archipelago-classify.py -o results.performance.constrained.csv   --describe results.constrained.txt   --opt 0 --true-model constrained   simulated-data/target.constrained.summary-stats.csv simulated-data/training.unconstrained.summary-stats.csv simulated-data/training.constrained.summary-stats.csv
