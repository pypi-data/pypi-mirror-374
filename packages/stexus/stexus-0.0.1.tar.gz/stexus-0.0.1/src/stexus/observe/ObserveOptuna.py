from optuna.storages import RDBStorage
from packaging import version
import optuna_dashboard._cli
import time
import os
# from optuna_dashboard._cli import auto_select_serer, run_debug_server, run_gunicorn, run_wsgiref, BaseStorage, get_storage
from .BaseObserve import BaseObserve
from .ObserveException import ObserveException
from ..config.Config import ConfigModel

class ObserveOptuna(BaseObserve):
    def __init__(self, config: ConfigModel|None = None) -> None:
        super().__init__(config)

    def observe(self, ignore_config_enabled: bool=False) -> None:
        # i am trying to understand
        # lib/python3.XX/site-packages/optuna_dashboard/_cli.py

        if not ignore_config_enabled and not self._config.get('observer', {}).get('enabled', False):
            print("observer is disabled")
            return
        
        storage: optuna_dashboard._cli.BaseStorage|None = None
        max_retry = 10
        while retry := 0 < max_retry and storage is None:
            try:
                storage = optuna_dashboard._cli.get_storage(
                    self._config["storage"],
                    # storage_class=args.storage_class # default node
                )
            except:
                time.sleep(3)
                print(f"observer: failed to get storage {self._config['storage']}, retried {retry}/{max_retry}.")
                retry = retry + 1

        if storage is None:
            raise ObserveException(f"observer: failed to get storage {self._config['storage']}, retried {max_retry}.")

        artifact_dir = self._config.get('observer', {}).get('artifact_dir')
        artifact_store: optuna_dashboard._cli.ArtifactStore | None
        if artifact_dir is None:
            artifact_store = None
        elif version.parse(optuna_dashboard._cli.optuna_ver) >= version.Version("3.3.0"):
            from optuna.artifacts import FileSystemArtifactStore

            artifact_store = FileSystemArtifactStore(artifact_dir)
        else:
            artifact_backend = optuna_dashboard._cli.FileSystemBackend(artifact_dir)
            artifact_store = optuna_dashboard._cli.ArtifactBackendToStore(artifact_backend)
        app = optuna_dashboard._cli.create_app(storage, artifact_store=artifact_store, debug=optuna_dashboard._cli.DEBUG)

        if optuna_dashboard._cli.DEBUG and isinstance(storage, RDBStorage):
            app = optuna_dashboard._cli.register_profiler_view(app, storage)

        server = optuna_dashboard._cli.auto_select_server(self._config.get('observer', {}).get('server')) # type: ignore
        if optuna_dashboard._cli.DEBUG:
            optuna_dashboard._cli.run_debug_server(
                app,
                self._config.get('observer', {}).get('host'),
                self._config.get('observer', {}).get('port'),
                self._config.get('observer', {}).get('quiet')
            )
        elif server == "wsgiref":
            optuna_dashboard._cli.run_wsgiref(
                app,
                self._config.get('observer', {}).get('host'),
                self._config.get('observer', {}).get('port'),
                self._config.get('observer', {}).get('quiet')
            )
        elif server == "gunicorn":
            optuna_dashboard._cli.run_gunicorn(
                app,
                self._config.get('observer', {}).get('host'),
                self._config.get('observer', {}).get('port'),
                self._config.get('observer', {}).get('quiet')
            )
        else:
            raise ObserveException("must not reach here")
