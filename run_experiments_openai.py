from const import ModelType
# from baseline_agent import main
from openai_baseline_agent import main as openai_main
# from bfcl_agent import main as bfcl_main
from logger import logger

models = [
    "gpt-4o-mini"
]

for model in models[:1]:
    model_str=model.replace(":", "_").replace(".", "_")
    print(f'----------------------- RUNNING EXPERIMENTS FOR MODEL: {model} ----------------------')
    openai_main(model=model, output_file=f"results_vllm_{model_str}.json")
    logger.reset()
    print(f'----------------------- COMPLETED EXPERIMENTS FOR MODEL: {model} ----------------')