# RUNNING INFERENCE EXPERIMETS - A GUIDE
This guide is for running the inference using our framework in order to generate a dataset of sequences of actions based on the provided dataset of prompts.

## Prerequisites
python>=3.10

## Instalation
```bash
git clone https://github.com/Bloodrock-AI/temp.git
```

```bash
pip install numpy torch transformers llm-tool accelerate
```
- More dependencies are needed based on the models that you are going to be using.

- We trust you to use the environment tools (uv, python-venv, conda) of your preference.

## Add your models
1. Add your model in the `ModeTypes` enum in `const.py`:
```python3
class ModelType(Enum):
    DEEPSCALE_R = "agentica-org/DeepScaleR-1.5B-Preview" # string is the same value as in hugging face
```
2. Add it to the experiment suite in `run_experiments.py`:
```python3
from const import ModelType
# ...

models = [
  ...
  ModelType.DEEPSCALE_R,
  ...
]
```

## Run the experiments
```bash
python3 run_experiments.py
```

This will produce 2 `json` files for each model.
1. `bfcl_results_<model_name>.json`: contains all the results (output sequences) from the BFCL-produced dataset.
2. `results_<model_name>.json`: contains all the results (output sequences) from our own dataset.

# MESSAGE TO STAMOULIS
You only need to produce the output sequences for the datasets for different models. We will be doing the rest of the work to get the actual metrics.
