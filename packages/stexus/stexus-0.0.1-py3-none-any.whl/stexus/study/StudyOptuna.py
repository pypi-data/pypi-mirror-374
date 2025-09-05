import optuna
from .BaseStudy import BaseStudy
from ..experiment.ExperimentInterface import ExperimentInterface
from ..config.Config import ConfigModel

class StudyOptuna(BaseStudy):
    def __init__(self,
                 config: ConfigModel|None = None,
                 experiment: ExperimentInterface|None = None
    ) -> None:
        super().__init__(config, experiment)

    def _objective(self, trial: optuna.Trial) -> float|int:
        score: float|int = self._experiment.experiment(trial)
        return score

    def study(self):
        # optuna.create_study(*, storage: str | BaseStorage | None = None, sampler: BaseSampler | None = None, pruner: BasePruner | None = None, study_name: str | None = None, direction: str | StudyDirection | None = None, load_if_exists: bool = False, directions: Sequence[str | StudyDirection] | None = None) -> Study
        study = optuna.create_study(
            study_name=self._config["study_name"],
            storage=self._config["storage"],
            direction=self._config["direction"],
            load_if_exists=self._config["load_if_exists"]
        )

        # optimize(func: ObjectiveFuncType, n_trials: int | None = None, timeout: float | None = None, n_jobs: int = 1, catch: Iterable[type[Exception]] | type[Exception] = (), callbacks: Iterable[(Study, FrozenTrial) -> None] | None = None, gc_after_trial: bool = False, show_progress_bar: bool = False) -> None
        study.optimize(
            func=self._objective,
            n_trials=self._config["trials"]
        )
