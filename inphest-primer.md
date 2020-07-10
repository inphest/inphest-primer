# Inphest

## Introduction

The Inphest pipeline consists of:

-   A simulator, used to generate training data, as well as known target/objective data for testing/development.
-   A calculator to produce target/objective data summary statistics from (empirical) data to be classified.
-   A classifier that takes the target/objective data and training data sets and produces the posterior weights of the candidate models

The current status of these are, respectively:

-   The simulator script, ``inphest-simulate.py``, is complete (though the summary statistics currently used are not demonstrated to be effective).
-   The calculator script has not yet been written, as we have yet to identify the summary statistics that are effective in the parameter space of concern to distinguish between the models that we are interested in.
-   We do not have a dedicated (Inphest-specific) classification script, because the [classification script](https://github.com/jeetsukumaran/archipelago/blob/master/bin/archipelago-classify.py) from the [Archipelago](https://github.com/jeetsukumaran/archipelago) package provides this service without modification. For final release we will port in this code and rename it appropriately (it is pretty much a drop-in otheport in this code and rename it appropriately (it is pretty much a drop-in otherwise).

## Workflow

### Overview

1.  Simulate the training data, e.g.

    ```
    $ inphest-simulate.py -H archipelago.histories.json -F archipelago model/constrained.inphest.json -z 891753306876133838
    $ inphest-simulate.py -H archipelago.histories.json -F archipelago model/unconstrained.inphest.json -z 891753306876133838
    ```

2.  Calculate summary statistics on the empirical data, or otherwise simulate the target data, e.g.:

    ```
    $ inphest-simulate.py -H archipelago.histories.json -F archipelago model/target1.inphest.json -z 891753306876133838
    ```

3.  Build a classifier using the training data and apply it to the target data, e.g.:

    ```
    $ archipelago-classify.py -o constrained.performance.csv --describe constrained.dapc.txt --opt 0 --true-model constrained data/target.csv data/constrained.csv data/unconstrained.csv
    ```

### Simulator Input Data

The Inphest pipeline requires:

1.  A history of host diversification and biogeographic events to condition the samples on
2.  A configuration file describing the symbiont model

#### Host History Specification

We would like to infer the host history from empirical data.
Currently, Inphest supports consuming the output of a RevBayes biogeographic analysis which includes the sampled histories of a system.
Unfortunately, this is coded against a very old version of RevBayes in which the biogeographic analysis (a) was broken; (b) fixes were pending but not immediately forthcoming; and (c) the output format for expressing the historic events was not stable, documented, meant for client consumption, and generally not to be relied upon.

To continue development of Inphest in the mean time, we turned to simulations to provide the host histories.
In particular, we used the [``--store-histories``](https://github.com/jeetsukumaran/archipelago/blob/master/bin/archipelago-simulate.py#L60-L63) option of [``archipelago-simulate.py``](https://github.com/jeetsukumaran/archipelago/blob/master/bin/archipelago-simulate.py) in the [Archipelago](https://github.com/jeetsukumaran/archipelago) package to generate the host history history file which can be consumed directly by Inphest.
Note that the host history data is also used to define the geographical system (area definitions) for both the host and the symbiont system.

An example of generating a host history for Inphest using Archipelago can be found in the ``examples/example1/`` directory.
The script ``examples/example1/bin/01-generate-host-histories.sh``:

```
$ archipelago-simulate.py --store-histories -n 1 model/host.archipelago.no_area_loss.json -o out/host
```

The file ``examples/example1/model/host.archipelago.no_area_loss.json`` is an *Archipelago* configuration file, specifying the biogeographical model that the host data will be simulated under.
The ``--store-histories`` flag specifies that, in addition to the normal output of trees etc., to also produce a "``<PREFIX>.histories.json``" file that can be passed directly to Inphest for processing.

#### Inphest Model Specification

The Inphest model can be specified by passing in either a JSON-format or Python format dictionary file, or, if the Inphest process is invoked from the library using a script, by passing in a Python dictionary directly.
The former is typically straight-forward if all information in the model is statically available in the dictionary itself.
For example, if a speciation or area gain rate is independent of the state of the simulation, or is a simple function of a trait state of a lineage.
Running the command:

```
$ inphest-simulate.py --create-example-model-file /path/to/model.json
```

generates a sample Inphest model file:

```
{
    "model_id": "Model1",
    "host_to_symbiont_time_scale_factor": 1.0,
    "diversification": {
        "mean_symbiont_lineage_birth_rate": 0.03,
        "lineage_birth_rate": {
            "definition_type": "lambda_definition",
            "definition": "lambda **kwargs: 1.00",
            "description": "fixed: 1.00"
        },
        "mean_symbiont_lineage_death_rate": 0.0,
        "lineage_death_rate": {
            "definition_type": "lambda_definition",
            "definition": "lambda **kwargs: 1.00",
            "description": "fixed: 1.00"
        }
    },
    "anagenetic_host_assemblage_evolution": {
        "mean_symbiont_lineage_host_gain_rate": 0.03,
        "symbiont_lineage_host_gain_weight": {
            "definition_type": "lambda_definition",
            "definition": "lambda **kwargs: 1.00",
            "description": "fixed: 1.00"
        },
        "mean_symbiont_lineage_host_loss_rate": 0.0,
        "symbiont_lineage_host_loss_weight": {
            "definition_type": "lambda_definition",
            "definition": "lambda **kwargs: 1.0",
            "description": "fixed: 1.0"
        }
    },
    "cladogenetic_host_assemblage_evolution": {
        "sympatric_subset_speciation_weight": 1.0,
        "single_host_vicariance_speciation_weight": 1.0,
        "widespread_vicariance_speciation_weight": 1.0,
        "founder_event_speciation_weight": 0.0
    },
    "anagenetic_geographical_range_evolution": {
        "mean_symbiont_lineage_area_gain_rate": 0.03,
        "symbiont_lineage_area_gain_weight": {
            "definition_type": "lambda_definition",
            "definition": "lambda **kwargs: 1.00",
            "description": "fixed: 1.00"
        },
        "mean_symbiont_lineage_area_loss_rate": 0.0,
        "symbiont_lineage_area_loss_weight": {
            "definition_type": "lambda_definition",
            "definition": "lambda **kwargs: 1.0",
            "description": "fixed: 1.0"
        }
    },
    "cladogenetic_geographical_range_evolution": {
        "sympatric_subset_speciation_weight": 1.0,
        "single_area_vicariance_speciation_weight": 1.0,
        "widespread_vicariance_speciation_weight": 1.0,
        "founder_event_speciation_weight": 0.0
    }
}
```

Note the definitions of the various rate weight function (lineage birth rates, symbiont lineage host gain rate, symbiont lineage area gain rates, etc.)
These are given here by (Python) lambda expressions that, in this example, return fixed values (of 1.00, i.e., not modifying the base rates in any way).
The lambda expressions take the following keyword arguments when called which can be used to calculate more complex values.
For example, the area gain weight function, which, when multipled with the base host gain rate determines the probability that a particular symbiont lineage will gain an area from its range has the following contract:

-   Input keyword arguments:
    -   ``symbiont_lineage``
    -   ``from_area``
    -   ``to_area``
    -   ``host``
    -   ``num_potential_new_area_infection_events``
    -   ``simulation_elapsed_time``
-   Returns:
    -   (float) Area gain rate weight.

This value will be the multiplied with the base area gain rate to obtain the probability that ``to_area`` is successfully added to the range of the symbiont lineage ``symbiont_lineage`` due to presence of host lineage ``host`` in both ``to_area`` and ``from_area``.
The ``num_potential_new_area_infection_events`` is there for normalization of rates, if needed, while ``simulation_elapsed_time`` is to allow for modeling of epochal change in rates.

Similarly, the host gain weight function has the following contract:

-   Input keyword arguments:
    -   ``symbiont_lineage``
    -   ``from_host_lineage``
    -   ``to_host_lineage``
    -   ``area``
    -   ``num_potential_new_host_infection_events``
    -   ``simulation_elapsed_time``
    -   ``symbiont_tree``
    -   ``host_system``
-   Returns:
    -   (float) Host gain rate weight.

This return value will be the multiplied with the base host gain rate to obtain the probability that ``to_host_lineage`` is successfully colonized by the symbiont lineage ``symbiont_lineage`` from ``from_host_lineage`` in the area ``area``.
The ``num_potential_new_area_infection_events`` is given to allow for normalization of weights, while ``simulation_elapsed_time`` is given to allow for modeling of epochal changes. ``symbiont_tree`` gives access to the growing symbiont phylogeny, while ``host_system`` gives access to data about the host system, which includes the host phylogeny.

All valid Python lambda expressions are supported.

It might be more useful to be allowed to calculate and return rate values in full Python functions.
The only way to do this is to write a dedicated script that defines the function(s) required and invokes the Inphest simulator via library calls.
This is shown below in the second case study.

### Simulator Output

The Inphest simulation produces a number of output files, including:

-   ``<OUTPUT-PREFIX>.summary-stats.csv``
-   ``<OUTPUT-PREFIX>.trees``
-   ``<OUTPUT-PREFIX>.model.log.json``
-   ``<OUTPUT-PREFIX>.log``

The main file of interest in the next and final stage of the pipeline is the "``.summary-stats.csv``" file, which is a plain text file consisting of rows of comma-separated data fields.
This will constitute the training data used to build the classifier.
Fields corresponding to summary statistics that are used as predictor variables or "features" all are prefixed with the string "predictor.", while the model label field is given as "model.id".
This structure allows the data to used as-is by the Archipelago classifier.

### Constructing and Applying the Classifier

Assuming that we have generated sets of data under each of the competing models (e.g., "model1", "model2", "model3") using the Inphest simulator, and have a set of summary statistics from the data we want to classify (e.g. "target.csv"), then invoking the Archipelago classifier will provide the final results:

```
$ archipelago-classify.py --opt 0 target.csv model1.summary-stats.csv model2.summary-stats.csv [model3.summary-stats.csv [model4.summary-stats.csv [...]]]
```

## Case Studies

### Case Study I: Simple (Illustrative)

```
$ inphest-simulate.py \
    -F archipelago -H data/host.histories.json \
    --model-format json model/inphest.model1.json \
    -n 300 \
    -o out/training-data.inphest1
$ inphest-simulate.py \
    -F archipelago -H data/host.histories.json \
    --model-format json model/inphest.model2.json \
    -n 300 \
    -o out/training-data.inphest2
$ inphest-simulate.py \
    -F archipelago -H data/host.histories.json \
    --model-format json model/inphest.model1.json \
    -n 1 \
    -o out/target-data.inphest1
$ archipelago-classify.py --opt 0 \
    out/target-data.inphest1.summary-stats.csv \
    out/training-data.inphest1.summary-stats.csv \
    out/training-data.inphest2.summary-stats.csv
```

### Case Study II: Geography vs. Phlogenetic Distance

This is one of the principal motivating cases for this project: identifying whether or not stochastic geographical history of hosts exclusively inform the phylogenetic co-structures of the host-parasite assemblages, or whether or not there are some phylogenetic constraints on new host acquistion.
For this, we define two models:

(1) the phylogenetically-constrained model, referred to more simply as the "constrained model", in which phylogenetic distance between the source and potential target host contributes to the probability of a successful host gain

and

(2) the phylogenetically-unconstrained model, referred to more simply as the "unconstrained model", in which the probability of a successful host gain is independent of the host distances.

These two models are identical in all respects except in the host gain weight function: in the constrained model, the base rate of gaining a host is weighted by the phylogenetic distance between the source and destination host, while in the unconstrained model it is not.
For the former case, we provide a custom Python function to return the host gain weight that calculates the host phylogenetic distance and appropriately weights the base rate:

```
def constrained_host_gain_weight(**kwargs):
    h1 = kwargs["from_host_lineage"].lineage_parent_id
    h2 = kwargs["to_host_lineage"].lineage_parent_id
    lineage_distance = kwargs["host_system"].host_lineage_distance_matrix[h1][h2]
    if lineage_distance == 0:
        assert h1 == h2
    lineage_distance += (kwargs["simulation_elapsed_time"] - kwargs["from_host_lineage"].start_time) + (kwargs["simulation_elapsed_time"] - kwargs["to_host_lineage"].start_time)
    rate = 1.0 / lineage_distance
    return rate
```

For the former case, we provide a custom Python function to return a flat host gain weight:

```
def unconstrained_host_gain_weight(**kwargs):
    return 1.0
```
The phylogeny-weighted function is difficult to express in a lambda expression, so we cannot use a JSON file to specify the Inphest model, which means we cannot invoke the stock Inpest simulator front-end script.
Instead, we use a custom simulation script that builds the model programmatically and invokes the Inphest simulator via library calls:

```
#! /usr/bin/env python

import sys
import random
import argparse
import inphest

def constrained_host_gain_weight(**kwargs):
    h1 = kwargs["from_host_lineage"].lineage_parent_id
    h2 = kwargs["to_host_lineage"].lineage_parent_id
    lineage_distance = kwargs["host_system"].host_lineage_distance_matrix[h1][h2]
    if lineage_distance == 0:
        assert h1 == h2
    lineage_distance += (kwargs["simulation_elapsed_time"] - kwargs["from_host_lineage"].start_time) + (kwargs["simulation_elapsed_time"] - kwargs["to_host_lineage"].start_time)
    rate = 1.0 / lineage_distance
    return rate

def unconstrained_host_gain_weight(**kwargs):
    return 1.0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_id",
            help="Model type: 'constrained' or 'unconstrained'")
    host_options = parser.add_argument_group("Host Biogeography Options")
    host_options.add_argument("-H", "--host-biogeographic-history",
            metavar="HOST-EVENT-FILE",
            default=None,
            help="Path to file providing the host biogeographic events.")
    host_options.add_argument("-F", "--host-biogeographic-history-format",
            choices=["revbayes", "archipelago"],
            default="revbayes",
            help="Format of the host biogeographic history.")
    output_options = parser.add_argument_group("Output Options")
    output_options.add_argument('-o', '--output-prefix',
        action='store',
        dest='output_prefix',
        type=str,
        default='inphest',
        metavar='OUTPUT-FILE-PREFIX',
        help="Prefix for output files (default: '%(default)s').")
    run_options = parser.add_argument_group("Run Options")
    run_options.add_argument("-n", "--nreps",
            type=int,
            default=10,
            help="Number of replicates (default: %(default)s).")
    run_options.add_argument("-z", "--random-seed",
            default=None,
            help="Seed for random number generator engine.")
    run_options.add_argument("--log-frequency",
            default=None,
            type=float,
            help="Frequency that background progress messages get written to the log (0: do not log informational messages).")
    run_options.add_argument("--file-logging-level",
            default="info",
            help="Message level threshold for file logs.")
    run_options.add_argument("--stderr-logging-level",
            default="info",
            help="Message level threshold for screen logs.")
    run_options.add_argument("--debug-mode",
            action="store_true",
            default=False,
            help="Run in debugging mode.")
    args = parser.parse_args()
    if args.host_biogeographic_history is None:
        sys.exit("Require path to host biogeographic history events to be specified.")
    if args.model_id not in ("constrained", "unconstrained"):
        sys.exit("Model ID must be either 'constrained' or 'unconstrained': {}".format(args.model_id))
    model_id = args.model_id
    if model_id == "constrained":
        host_gain_weight_fn = constrained_host_gain_weight
    else:
        host_gain_weight_fn = unconstrained_host_gain_weight
    model = {
        "model_id": model_id,
        "host_to_symbiont_time_scale_factor": 1.0,
        "diversification": {
            "mean_symbiont_lineage_birth_rate": 0.01,
            "lineage_birth_rate": {
                "definition_type": "lambda_definition",
                "definition": "lambda **kwargs: 1.00",
                "description": "fixed: 1.00"
            },
            "mean_symbiont_lineage_death_rate": 0.0,
            "lineage_death_rate": {
                "definition_type": "lambda_definition",
                "definition": "lambda **kwargs: 1.00",
                "description": "fixed: 1.00"
            }
        },
        "anagenetic_host_assemblage_evolution": {
            "mean_symbiont_lineage_host_gain_rate": 0.02,
            "symbiont_lineage_host_gain_weight": {
                "definition_type": "function_object",
                "definition": host_gain_weight_fn,
                "description": "fixed: 1.00"
            },
            "mean_symbiont_lineage_host_loss_rate": 0.01,
            "symbiont_lineage_host_loss_weight": {
                "definition_type": "lambda_definition",
                "definition": "lambda **kwargs: 1.0",
                "description": "fixed: 1.0"
            }
        },
        "cladogenetic_host_assemblage_evolution": {
            "sympatric_subset_speciation_weight": 1.0,
            "single_host_vicariance_speciation_weight": 1.0,
            "widespread_vicariance_speciation_weight": 1.0,
            "founder_event_speciation_weight": 0.0
        },
        "anagenetic_geographical_range_evolution": {
            "mean_symbiont_lineage_area_gain_rate": 0.1,
            "symbiont_lineage_area_gain_weight": {
                "definition_type": "lambda_definition",
                "definition": "lambda **kwargs: 1.00",
                "description": "fixed: 1.00"
            },
            "mean_symbiont_lineage_area_loss_rate": 0.01,
            "symbiont_lineage_area_loss_weight": {
                "definition_type": "lambda_definition",
                "definition": "lambda **kwargs: 1.0",
                "description": "fixed: 1.0"
            }
        },
        "cladogenetic_geographical_range_evolution": {
            "sympatric_subset_speciation_weight": 1.0,
            "single_area_vicariance_speciation_weight": 1.0,
            "widespread_vicariance_speciation_weight": 1.0,
            "founder_event_speciation_weight": 0.0
        }
    }
    inphest.run(
            output_prefix=args.output_prefix,
            nreps=args.nreps,
            host_history_samples_path=args.host_biogeographic_history,
            host_history_samples_format=args.host_biogeographic_history_format,
            model_definition_source=model,
            model_definition_type="python-dict",
            random_seed=args.random_seed,
            stderr_logging_level=args.stderr_logging_level,
            file_logging_level=args.file_logging_level,
            debug_mode=args.debug_mode
            )

if __name__ == "__main__":
    main()
```

Given the above in a script, e.g., "``simulate.py``", the following shell script encapsulates the entire pipeline for an analysis, including generating the training data, the (simulated) test data, and evaluating the results:

```
python ../../bin/simulate.py --nreps 100 -o data/target.unconstrained --debug -F archipelago -H ../../data/01-simulated-host-histories/H001.reps1.histories.json unconstrained  && \
    python ../../bin/simulate.py --nreps 100 -o data/target.constrained --debug -F archipelago -H ../../data/01-simulated-host-histories/H001.reps1.histories.json constrained && \
    python ../../bin/simulate.py --nreps 100 -o data/training.unconstrained --debug -F archipelago -H ../../data/01-simulated-host-histories/H001.reps1.histories.json unconstrained && \
    python ../../bin/simulate.py --nreps 100 -o data/training.constrained --debug -F archipelago -H ../../data/01-simulated-host-histories/H001.reps1.histories.json constrained && \
    archipelago-classify.py -o results.performance.unconstrained.csv --describe results.unconstrained.txt --opt 0 --true-model unconstrained data/target.unconstrained.summary-stats.csv data/training.unconstrained.summary-stats.csv data/training.constrained.summary-stats.csv && \
    archipelago-classify.py -o results.performance.constrained.csv   --describe results.constrained.txt   --opt 0 --true-model constrained   data/target.constrained.summary-stats.csv data/training.unconstrained.summary-stats.csv data/training.constrained.summary-stats.csv
```
