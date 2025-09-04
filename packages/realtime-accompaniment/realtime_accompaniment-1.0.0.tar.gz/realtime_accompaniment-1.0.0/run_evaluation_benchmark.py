import numpy as np
import argparse
from utils.evaluation import evaluation
from utils.presets import get_config, get_presets


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Run evaluation benchmark with configurable parameters"
    )
    parser.add_argument(
        "--num_iterations",
        type=int,
        default=10,
        help="Number of iterations for each config (default: 10)",
    )
    parser.add_argument(
        "--param_name",
        type=str,
        default="lag",
        help="Parameter name to sweep (default: lag)",
    )
    parser.add_argument(
        "--start_value",
        type=float,
        default=0,
        help="Start value of the parameter (default: 0)",
    )
    parser.add_argument(
        "--end_value",
        type=float,
        default=1000,
        help="End value of the parameter (default: 1000)",
    )
    parser.add_argument(
        "--step",
        type=float,
        default=100,
        help="Step size of the parameter (default: 100)",
    )
    parser.add_argument(
        "--eval_mode",
        nargs="+",
        type=str,
        default=["random", "continuous", "segmented"],
        help="Evaluation mode(s) to use (default: random continuous segmented)",
    )
    parser.add_argument(
        "--eval_system",
        nargs="+",
        type=str,
        default=["noa", "dtw", "match"],
        help="Evaluation system(s) to use (default: noa dtw match)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # get the possible configs to evaluate on
    possible_configs = get_presets()[
        1:-2
    ]  # exclude the last two configs (they are not valid configs)
    for config in possible_configs:
        solo_reference, orch_reference, _ = get_config(config)

        # evaluate on the config
        for eval_mode in args.eval_mode:  # iterate over evaluation modes
            smod_eval_info, mode_array = evaluation.generate_smod_evaluation(
                orch_reference,
                solo_reference,
                num_iterations=args.num_iterations,
                plot_each=False,
                outfile_name=config,
                eval_mode=eval_mode,
            )
            param_values = np.arange(
                args.start_value, args.end_value, args.step
            )  # doesn't include end_value

            for eval_system in args.eval_system:  # iterate over evaluation systems
                if eval_system == "match":
                    # match requires the query and references to be the same audio format
                    # since our queries are mono, we need to use the mono version of the references
                    actual_solo_ref = solo_reference[:-4] + "_mono.wav"
                    actual_orch_ref = orch_reference[:-4] + "_mono.wav"
                else:
                    actual_solo_ref = solo_reference
                    actual_orch_ref = orch_reference

                err_dict_list = evaluation.generate_batch_stsm_evaluation(
                    smod_eval_info=smod_eval_info,
                    solo_ref=actual_solo_ref,
                    orch_ref=actual_orch_ref,
                    mode_array=mode_array,
                    save_results=True,
                    outfile_name=config,
                    param_name=args.param_name,
                    param_values=param_values,
                    eval_mode=eval_mode,
                    eval_system=eval_system,
                )
