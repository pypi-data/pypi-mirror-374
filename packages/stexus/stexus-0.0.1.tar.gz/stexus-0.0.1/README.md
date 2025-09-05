# Stexus

*Study, Experiment, adjUst, Study*

A flexible optimization tool that connects (hyper)parameter optimization engines with custom experiments through template-based configuration and a task, e.g. scripting.

Stexus enables you to optimize any parameterized process by:

- Rendering template files with trial parameters.
- Executing custom experiment scripts.
- Collecting and optimizing results.
- Rendering template files with optimized trial parameters.
- (Repeat.)

Currently supported engines:

- Optuna ([optuna.org](https://optuna.org/))

We use Jinja ([site](https://jinja.palletsprojects.com/en/stable/)) for our templating engine.

## Why Stexus?

Existing hyperparameter optimization tools are typically designed for specific use cases, primarily machine learning workflows. This leaves a significant gap in automation: **there is no general purpose solution for optimizing parameters in arbitrary processes**.

Whether it's tuning system configurations, optimizing algorithm parameters in different languages, or finding optimal settings for complex services, often we are left to manually iterate or build custom optimization script from scratch.

Stexus bridges this gap by providing general-purpose parameter optimization tool that can work with arbitrary processes, like scripting. By combining template rendering with an optimization engines, Stexus enables dynamic experimentation across diverse domains and technologies.

Stexus takes the stance on anything that can be parameterized, can be optimized, therefore enabling wider parameter optimization tasks.

## Installation

You can install Stexus via `pip` (we are on [PyPI](https://pypi.org/p/stexus)!)

```sh
python3 -m pip install stexus
```

## Quick Start

1. Create your experiment template (e.g., `config_template.yaml`, `config.txt`, whatever that is desired). 
    
    For example, this is the content of template containing single number that will be read into a linux shell script:

    ```
    {{ number1 }}
    ```

2. Create your experiment script (e.g., `guess.sh`):
    ```bash
    #!/bin/bash
    number=55
    guess=$(cat config.txt)
    diff=$((number > guess ? number - guess : guess - number))
    sleep 1 # does not have to have sleep, this is just so that
            # observer has time to spawn
    echo "$diff" >./result # write metric to the score file
    ```

    (or you can combine 1 and 2 together, so that experiment is using rendered script directly)

3. Configure Stexus (`config.yaml`):

    ```yaml
    study_name: "My Optimization Study"
    engine: optuna
    trials: 50
    source_templates:
      - ./config.txt
    rendered_templates_path: rendered
    score_path: ./result
    storage: sqlite:///study.sqlite3
    direction: minimize
    experiment:
      type: script
      args: ./guess.sh
    adjustments:
      - name: number1
        type: int
        config:
          low: 1
          high: 50
    ```

4. Run the optimization:

    ```bash
    python3 -m stexus -c config.yaml
    ```

Or, go to one of the [examples](./example/) and run `python3 -m stexus -c config.yaml` to see how Stexus run.

## Usage

### Basic Usage

```bash
python3 -m stexus -c <config_file_path>
```

### Observer Mode

Monitor an existing study without running new trials:
```bash
python3 -m stexus -c <config_file_path> --observe-only
```

## Configuration Reference

Stexus uses YAML configuration files. All required fields must be specified.

### Core Settings

#### `study_name` (required)
- **Type**: string
- **Description**: Unique identifier for your optimization study

#### `engine` 
- **Type**: string
- **Default**: `optuna`
- **Allowed values**: `optuna`
- **Description**: Optimization backend engine

#### `trials` (required)
- **Type**: integer
- **Minimum**: 1
- **Description**: Number of optimization trials to run

#### `direction` (required)
- **Type**: string
- **Allowed values**: `minimize`, `maximize`
- **Description**: Optimization direction for the objective function

### Storage & Persistence

#### `storage` (required)
- **Type**: string
- **Description**: Backend storage URL (follows Optuna storage format)
- **Example**: `sqlite:///study.db`, `postgresql://user:pass@host/db`

#### `load_if_exists`
- **Type**: boolean
- **Default**: `true`
- **Description**: Whether to resume existing studies with the same name

### Template System

#### `source_templates` (required)
- **Type**: list of strings
- **Minimum length**: 1
- **Description**: Files or directories containing Jinja template files
- **Example**: `["./config.yaml.j2", "./scripts/"]`

#### `rendered_templates_path`
- **Type**: string
- **Default**: `rendered`
- **Description**: Directory where rendered templates will be saved

### Experiment Configuration

#### `experiment` (required)
- **Type**: object
- **Description**: Defines how experiments are executed

**Script Type** (currently the only supported type):
```yaml
experiment:
  type: script                    # required
  args: "./run_experiment.sh"     # required - script to execute
  ignore_exit_code: false         # optional, default: false
```

- **`type`**: Must be `script`
- **`args`**: Path to script or command to execute for each trial
- **`ignore_exit_code`**: If `true`, non-zero exit codes won't fail the trial

### Results

#### `score_path` (required)
- **Type**: string  
- **Description**: File path where the experiment writes the objective value
- **Note**: Must contain a single numeric value

### Parameter Space

#### `adjustments` (required)
- **Type**: list of parameter objects
- **Minimum length**: 1
- **Description**: Defines the parameter search space

Each parameter object must have `name`, `type`, and `config` fields:

**Integer Parameters:**
```yaml
- name: batch_size
  type: int
  config:
    low: 16        # required
    high: 128      # required  
    step: 16       # optional
    log: false     # optional, default: false
```

**Float Parameters:**
```yaml
- name: learning_rate
  type: float
  config:
    low: 0.001     # required
    high: 0.1      # required
    step: 0.001    # optional
    log: true      # optional, default: false (use log scale)
```

**Categorical Parameters:**
```yaml
- name: optimizer
  type: categorical
  config:
    choices: ["adam", "sgd", "rmsprop"]  # required, min 1 choice
```

**Uniform Distribution:**
```yaml
- name: dropout_rate
  type: uniform
  config:
    low: 0.0       # required
    high: 0.5      # required
```

**Log-Uniform Distribution:**
```yaml
- name: weight_decay
  type: loguniform
  config:
    low: 1e-5      # required  
    high: 1e-2     # required
```

**Discrete Uniform:**
```yaml
- name: hidden_size
  type: discrete_uniform
  config:
    low: 64.0      # required
    high: 512.0    # required
    q: 64.0        # required (step size)
```

### Observer (Study Monitoring)

#### `observer`
- **Type**: object
- **Description**: Configuration for study observation and monitoring

```yaml
observer:
  enabled: false              # default: false
  host: "127.0.0.1"          # default: "127.0.0.1"  
  port: 8080                 # default: 8080
  server: auto               # default: "auto"
  artifact_dir: "./artifacts" # optional
  storage_class: "RDBStorage" # optional  
  quiet: false               # default: false
```

- **`enabled`**: Whether to enable the observer
- **`host`**: Host address for the observer server
- **`port`**: Port for the observer server  
- **`server`**: Server type (typically leave as "auto")
- **`artifact_dir`**: Directory for storing artifacts
- **`storage_class`**: Storage class for the observer
- **`quiet`**: Suppress observer output


## How It Works

In stages, Stexus do:

1. **Template Rendering**

    Stexus processes your template files, replacing parameter placeholders with trial values

2. **Experiment Execution**

    Runs your specified script or command with the rendered templates

3. **Result Collection**

    Reads the objective value from the specified score file

4. **Optimization**

    Uses the configured engine to suggest better parameters for the next trial

This repeats until the specified number of trials is complete.

## Use Cases

Well, you can:

- Find optimal settings for applications or services via system configurations. Or other configuration.
- Optimize parameters for custom algorithms, choose it yourself.
- Find optimal resource allocation settings in infrastructure or deployment that you have.
- Basically optimizing any process that can be scripted and measured.

## Contributing

TODO

## License

See [LICENSE](./LICENSE).
