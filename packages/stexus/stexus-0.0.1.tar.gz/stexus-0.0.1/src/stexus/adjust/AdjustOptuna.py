import os
from optuna import Trial
from pathlib import Path
from typing import TypedDict, no_type_check
from jinja2 import Environment, Template, FileSystemLoader, select_autoescape
from .BaseAdjust import BaseAdjust
from .AdjustException import AdjustException
from ..config.Config import ConfigModel

class AdjustOptuna(BaseAdjust):
    def __init__(self, config: ConfigModel|None = None) -> None:
        super().__init__(config)

    def adjust(self, advocator: Trial) -> None:
        if self._source_template_environments is None:
            return

        adjusted_template_value = self._get_adjusted_template_value(advocator)
        for template in self._source_template_environments:
            if template['is_file']:
                if template['filename'] is not None:
                    tpl: Template = template['environment'].get_template(template['filename'])
                    stream = tpl.stream(**adjusted_template_value)  
                    rendered_path = Path(template['rendered_path']).joinpath(template['filename']) 
                    stream.dump(str(rendered_path))
            else:
                # a path

                # For each directory in the directory tree rooted at top (including top itself, but excluding '.' and '..'), yields a 3-tuple
                #     dirpath, dirnames, filenames
                for _, _, files in os.walk(template['path']):
                    for filename in files:
                        tpl: Template = template['environment'].get_template(filename)
                        stream = tpl.stream(**adjusted_template_value)
                        rendered_path = Path(template['rendered_path']).joinpath(filename)
                        stream.dump(str(rendered_path))

    @no_type_check # my vscode keeps hinting at wrong types
    def _get_adjusted_template_value(self, advocator: Trial) -> dict:
        adjusted_template_value={}
        for config in self._config['adjustments']:
            val = None
            metaconfig = config['config']

            if config['type'] == 'int':
                run_args = {
                    'name': config['name'],
                    'low': metaconfig['low'],
                    'high': metaconfig['high']
                }
                
                if metaconfig.get('step') is not None:
                    run_args['step'] = metaconfig['step']
                if metaconfig.get('log') is not None:
                    run_args['log'] = metaconfig['log']

                val = advocator.suggest_int(**run_args)
            elif config['type'] == 'float':
                run_args = {
                    'name': config['name'],
                    'low': metaconfig['low'],
                    'high': metaconfig['high']
                }
                
                if metaconfig.get('step') is not None:
                    run_args['step'] = metaconfig['step']
                if metaconfig.get('log') is not None:
                    run_args['log'] = metaconfig['log']

                val = advocator.suggest_float(**run_args)
            elif config['type'] == 'categorical':
                val = advocator.suggest_categorical(
                    name=config['name'],
                    choices=metaconfig['choices']
                )
            elif config['type'] == 'uniform':
                val = advocator.suggest_uniform(
                    name=config['name'],
                    low=metaconfig['low'],
                    high=metaconfig['high']
                )
            elif config['type'] == 'discrete_uniform':
                val = advocator.suggest_discrete_uniform(
                    name=config['name'],
                    low=metaconfig['low'],
                    high=metaconfig['high'],
                    q=metaconfig['q']
                )
            elif config['type'] == 'loguniform':
                val = advocator.suggest_loguniform(
                    name=config['name'],
                    low=metaconfig['low'],
                    high=metaconfig['high']
                )

            if val is None: continue
            adjusted_template_value[config['name']] = val

        return adjusted_template_value
