from const import ModelType
# from baseline_agent import main
from hf_baseline_agent import main as hf_main
# from bfcl_agent import main as bf\cl_main
from logger import logger

models = [
    # ModelType.QWEN_8B, # not supported
    ModelType.QWEN_14B,
    ModelType.QWEN_32B,
    ModelType.DEEPSEEK_R1,
    # ModelType.LLAMA_3_3_70B, # does weird stuff
]

for model in models:
    print(f'----------------------- RUNNING EXPERIMENTS FOR MODEL: {model} ----------------------')
    hf_main(model=model, output_file=f"results_{model}.json")
    logger.reset()
    # bfcl_main(model=model, output_file=f"bfcl_results_{model}.json")
    # logger.reset()
    print(f'----------------------- COMPLETED EXPERIMENTS FOR MODEL: {model} ----------------')