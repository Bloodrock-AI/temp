from const import ModelType
# from baseline_agent import main
from vllm_baseline_agent import main as vllm_main
# from bfcl_agent import main as bfcl_main
from logger import logger

models = [
    "qwen3:1.7b",
    "qwen3:0.6b",
    "qwen2.5:0.5b",
    "qwen3:8b"
]

for model in models[:1]:
    model_str=model.replace(":", "_").replace(".", "_")
    print(f'----------------------- RUNNING EXPERIMENTS FOR MODEL: {model} ----------------------')
    vllm_main(model=model, output_file=f"results_vllm_{model_str}.json")
    logger.reset()
    print(f'----------------------- COMPLETED EXPERIMENTS FOR MODEL: {model} ----------------')