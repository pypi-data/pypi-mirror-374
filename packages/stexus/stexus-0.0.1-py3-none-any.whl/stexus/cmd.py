import argparse
import multiprocessing as mp
import pprint

from .adjust.AdjustOptuna import AdjustOptuna
from .adjust.AdjustInterface import AdjustInterface
from .config.Config import Config, ConfigModel
from .experiment.ExperimentWithScript import ExperimentWithScript
from .experiment.ExperimentInterface import ExperimentInterface
from .study.StudyOptuna import StudyOptuna
from .study.StudyInterface import StudyInterface
from .observe.ObserveOptuna import ObserveOptuna
from .observe.ObserveInterface import ObserveInterface

def _get_experiment(config: ConfigModel, adjust: AdjustInterface) -> ExperimentInterface:
    if config['experiment']['type'] == 'script':
        return ExperimentWithScript(config, adjust)
    else:
        raise Exception(f"experiment.type {config['experiment']['type']} is not supported yet.")

def _get_study(config: ConfigModel) -> StudyInterface:
    if config['engine'] == 'optuna':
        adjust = AdjustOptuna(config)
        experiment = _get_experiment(config, adjust)
        return StudyOptuna(config, experiment)
    else:
        raise Exception(f"engine {config['engine']} is not supported yet.")

def _get_observe(config: ConfigModel) -> ObserveInterface:
    if config['engine'] == 'optuna':
        return ObserveOptuna(config)
    else:
        raise Exception(f"engine {config['engine']} is not supported yet.")

def run() -> None:
    parser = argparse.ArgumentParser(
        prog="stexus",
        description="Automated best parameter finder.",
    )
    parser.add_argument("--config", '-c', help="Configuration file path in YAML.", type=str, required=True)
    parser.add_argument("--observe-only", help="Run observer only.", action="store_true")

    args = parser.parse_args()

    config = Config(args.config).get_parsed_config()
    print("Config is:")
    pprint.pp(config)

    if args.observe_only:
        observe = _get_observe(config)
        observer = mp.Process(target=observe.observe, args=(True,)) # ignore_config_enabled

        observer.start()
        observer.join()
    else:
        study = _get_study(config)
        student = mp.Process(target=study.study)

        observe = _get_observe(config)
        observer = mp.Process(target=observe.observe)

        # start student first
        student.start()

        # then the observer
        observer.start()

        # wait until student is done
        student.join()

        # terminate observer after student is done
        # so that it does not KEEP RUNNING
        observer.terminate()
        observer.join()
