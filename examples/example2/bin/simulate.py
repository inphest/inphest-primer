#! /usr/bin/env python

import sys
import random
import argparse
import inphest


# symbiont_lineage
# from_host_lineage
# to_host_lineage
# area
# num_potential_new_host_infection_events
# symbiont_tree
# host_system
# simulation_elapsed_time
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
