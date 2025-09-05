import os
from optuna import Trial
from pathlib import Path
from typing import TypedDict
from abc import abstractmethod
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .AdjustInterface import AdjustInterface
from .AdjustException import AdjustException
from ..config.Config import ConfigModel

class JinjaPathEnvironments(TypedDict):
    rendered_path: str
    path: str
    filename: str|None
    is_file: bool
    environment: Environment

class BaseAdjust(AdjustInterface):
    _config: ConfigModel
    _source_template_environments: list[JinjaPathEnvironments] = []

    """
    Can accept file(s) and directory for source template,
    and then rendered source template will be placed on `rendered`
    directory, which is placed on same directory as

    DOES NOT read any subdirectory in source template path.

    source template's basedir if file, same dir if a dir.
    """
    def __init__(self,
                 config: ConfigModel|None = None
    ) -> None:
        super().__init__()
        if config is None:
            raise AdjustException("config cannot be empty.")
        self._config = config

        for path in self._config['source_templates']:
            if not os.path.exists(path):
                raise AdjustException(f"{path} as source_template must exists.")

            is_file = True
            filename = None
            if os.path.isdir(path):
                is_file = False
                basedir = Path(path).absolute()
            else:
                basedir = Path(path).parent.absolute()
                filename = Path(path).name

            rendered_path = Path(basedir).joinpath(self._config.get('rendered_templates_path', 'rendered'))
            rendered_path.mkdir(parents=True, exist_ok=True)
            self._source_template_environments.append({
                'is_file': is_file,
                'filename': filename,
                'path': str(basedir),
                'rendered_path': str(rendered_path),
                'environment': Environment(
                    loader=FileSystemLoader(basedir),
                    autoescape=select_autoescape(),
                    keep_trailing_newline=True,
                    # trim_blocks=False,
                    # lstrip_blocks=False
                )
            })

    @abstractmethod
    def adjust(self, advocator: Trial) -> None:
        pass
