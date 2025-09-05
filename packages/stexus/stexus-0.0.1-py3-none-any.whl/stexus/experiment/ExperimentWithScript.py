import subprocess
from optuna import Trial
from .BaseExperiment import BaseExperiment
from .ExperimentException import ExperimentException
from ..config.Config import ConfigModel
from ..adjust.AdjustInterface import AdjustInterface

class ExperimentWithScript(BaseExperiment):
    def __init__(self,
                 config: ConfigModel|None = None,
                 adjust: AdjustInterface|None = None
    ) -> None:
        super().__init__(config, adjust)

    def _run_script(self) -> None:
        subprocess.run(
            args=self._config["experiment"]["args"],
            check=not self._config["experiment"].get("ignore_exit_code", False),
            shell=True,
        )

    def _get_score(self) -> float:
        with open(self._config["score_path"], "r") as f:
            first_line = f.readline()

        return float(first_line)

    """
    returns score
    either in int or float.
    """
    def experiment(self, advocator: Trial) -> float|int:
        self._adjust.adjust(advocator)
        self._run_script()
        return self._get_score()
