import os
import yaml
from typing import TypedDict
from cerberus.validator import Validator, BareValidator
from optuna_dashboard._cli import SERVER_CHOICES as OPTUNA_SERVER_CHOICES
from typing import Literal, Union, Optional, Sequence, Final
from .ConfigException import ConfigException

# more flexible than the actual used stored config
# this is more like for parsing validation
class ConfigAdjustmentMetaconfigModel(TypedDict):
    """
    list of methods in mind:
        Trial.suggest_discrete_uniform(name: str, low: float, high: float, q: float) -> float
        Trial.suggest_loguniform(name: str, low: float, high: float) -> float
        Trial.suggest_uniform(name: str, low: float, high: float) -> float
        Trial.suggest_categorical(name: str, choices: Sequence[None]) -> None
        Trial.suggest_float(name: str, low: float, high: float, *, step: float | None = None, log: bool = False) -> float
        Trial.suggest_int(name: str, low: int, high: int, *, step: int = 1, log: bool = False) -> int
    """
    low: Optional[Union[float,int]]
    high: Optional[Union[float,int]]
    q: Optional[Union[float,int]]
    step: Optional[Union[float,int]]
    log: Optional[bool]
    choices: Optional[Sequence]

class ConfigAdjustmentModel(TypedDict):
    name: str
    type: Literal[
        'int',
        'float',
        'categorical',
        'uniform',
        'loguniform',
        'discrete_uniform',
    ]
    config: ConfigAdjustmentMetaconfigModel

class ConfigExperimentModel(TypedDict):
    type: Literal['script']
    args: str
    ignore_exit_code: bool

class ConfigObserverModel(TypedDict):
    enabled: bool
    host: str
    port: int
    server: str
    artifact_dir: str
    storage_class: str
    quiet: bool

class ConfigModel(TypedDict):
    adjustments: list[ConfigAdjustmentModel]

    # read score from experiments with a single file
    # created from experiment.
    # score is either int or float.
    # if there's multiple lines in the file,
    # first line will be used.
    # if `,` is used as decimal separator,
    # it will be replaced with `.` to conform with
    # python float.
    # multiple decimal separator in a number
    # may cause error.
    engine: Literal['optuna']
    score_path: str
    experiment: ConfigExperimentModel
    source_templates: list[str]
    rendered_templates_path: str
    observer: ConfigObserverModel

    # https://optuna.readthedocs.io/en/stable/reference/generated/optuna.study.create_study.html
    # similar to what optuna wants on create_study
    study_name: str
    trials: int
    storage: str
    load_if_exists: bool
    direction: Literal['minimize','maximize']
    # not supporting directions for now because it's confusing,
    # and i don't know how to do pydantic conditionally

# TODO max can be lower than min, shouldn't be like that
ConfigSchema: Final[dict] = {
    'study_name': {
        'required': True,
        'type': 'string',
    },
    'engine': {
        'type': 'string',
        'allowed': ['optuna'],
        'default': 'optuna',
    },
    'trials': {
        'required': True,
        'type': 'integer',
        'min': 1,
    },
    'score_path': {
        'required': True,
        'type': 'string'
    },
    'storage': {
        'required': True,
        'type': 'string'
    },
    'load_if_exists': {
        'type': 'boolean',
        'default': True
    },
    'direction': {
        'required': True,
        'type': 'string',
        'allowed': [
            'minimize',
            'maximize',
        ]
    },
    'source_templates': {
        'required': True,
        'type': 'list',
        'minlength': 1,
        'schema': {
            'type': 'string'
        }
    },
    'rendered_templates_path': {
        'type': 'string',
        'default': 'rendered'
    },
    'experiment': {
        'required': True,
        'type': 'dict',
        # this is oneof_schema so that we may expand it later if needed
        'oneof_schema': [
            {
                # script is executed with
                # subprocess.run(..., shell=True)
                'type': {'required': True, 'type': 'string', 'allowed': ['script'] },
                'args': {'required': True, 'type': 'string' }, # can be like a path to it
                'ignore_exit_code': {
                    'type': 'boolean',
                    'default': False
                }, # whether ignore if script gives non-zero exit code
                   # or something like that
                   # TODO need to figure out default for oneof_schema like this
                   # maybe coerce will work? Nope.
                   # also because i keep forgetting stuff: https://www.w3schools.com/python/python_lambda.asp
                   # just keep typing the default, we will try to make it work.
            },
        ],
    },
    'observer': {
        'type': 'dict',
        # this is oneof_schema so that we may expand it later if needed
        'schema': {
            'enabled': {'type': 'boolean', 'default': False },
            'host': {'required': True, 'type': 'string', 'default': '127.0.0.1' },
            'port': {'required': True, 'type': 'integer', 'default': 8080 },
            'server': {'type': 'string', 'allowed': OPTUNA_SERVER_CHOICES, 'default': 'auto' },
            'artifact_dir': {'type': 'string' },
            'storage_class': {'type': 'string' },
            'quiet': {'type': 'boolean', 'default': False },
        },
    },
    'adjustments': {
        # https://docs.python-cerberus.org/validation-rules.html#schema-list
        'required': True,
        'type': 'list',
        'minlength': 1,
        'schema': {
            'type': 'dict',
            # https://docs.python-cerberus.org/validation-rules.html#of-rules
            # https://docs.python-cerberus.org/validation-rules.html#of-rules-typesaver
            # i want to use oneof_schema
            # damn i cannot automatically normalize this
            'oneof_schema': [
                {
                    'name': {'required': True, 'type': 'string' },
                    'type': {
                        'required': True,
                        'type': 'string',
                        'allowed': ['discrete_uniform']
                    },
                    'config': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            # suggest_discrete_uniform
                            'low': {'required': True, 'type': 'float' },
                            'high': {'required': True, 'type': 'float' },
                            'q': {'required': True, 'type': 'float' },
                        },
                    }
                },
                {
                    'name': {'required': True, 'type': 'string' },
                    'type': {
                        'required': True,
                        'type': 'string',
                        'allowed': ['loguniform', 'uniform']
                    },
                    'config': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            # suggest_loguniform
                            # suggest_uniform
                            'low': {'required': True, 'type': 'float' },
                            'high': {'required': True, 'type': 'float' },
                        }
                    }
                },
                {
                    'name': {'required': True, 'type': 'string' },
                    'type': {
                        'required': True,
                        'type': 'string',
                        'allowed': ['categorical']
                    },
                    'config': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            # suggest_categorical
                            'choices': {'required': True, 'type': 'list', 'minlength': 1 },
                        }
                    }
                },
                {
                    'name': {'required': True, 'type': 'string' },
                    'type': {
                        'required': True,
                        'type': 'string',
                        'allowed': ['float']
                    },
                    'config': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            # suggest_float
                            'low': {'required': True, 'type': 'float' },
                            'high': {'required': True, 'type': 'float' },
                            'step': {'type': 'float', 'default': None },
                            'log': {'type': 'boolean', 'default': False },
                        }
                    }
                },
                {
                    'name': {'required': True, 'type': 'string' },
                    'type': {
                        'required': True,
                        'type': 'string',
                        'allowed': ['int']
                    },
                    'config': {
                        'required': True,
                        'type': 'dict',
                        'schema': {
                            # suggest_int
                            'low': {'required': True, 'type': 'integer' },
                            'high': {'required': True, 'type': 'integer' },
                            'step': {'type': 'integer', 'default': None },
                            'log': {'type': 'boolean', 'default': False },
                        }
                    }
                },
            ],
        }
    }
}

class Config():
    _config: ConfigModel

    def __init__(self, config_file: str) -> None:
        if not os.path.exists(config_file):
            raise ConfigException(f"{config_file} as config_file must exists.")
        with open(config_file, 'r') as f:
            parsed = yaml.safe_load(f)

        v: BareValidator = Validator() # type: ignore
        if v.validate(document=parsed, schema=ConfigSchema):
            # idk
            normalized = v.normalized(document=parsed, schema=ConfigSchema)
            self._config = ConfigModel(**normalized) # type: ignore

            # then we normalize what is not normalized by cerberus
            # afaik anything that's in *of.
            if self._config.get('experiment').get('ignore_exit_code') is None:
                self._config.get('experiment')['ignore_exit_code'] = False
            for adjustment in self._config['adjustments']:
                if adjustment.get('config').get('step') is None:
                    # if does not exists, set to none
                    # i know this looks weird, trust.
                    adjustment.get('config')['step'] = None
                if adjustment.get('config').get('log') is None:
                    adjustment.get('config')['log'] = False
        else:
            raise ConfigException(f"error(s) when validating config: {v.errors}")

    def get_parsed_config(self) -> ConfigModel:
        return self._config
