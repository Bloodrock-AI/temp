from const import ModelType
from baseline_agent import main
from logger import logger

models = [
    ModelType.QWEN_0_5B,
    ModelType.DEEPSEEK_1_5B,
    # ModelType.QWEN_7B,
    # ModelType.DEEPSEEK_QWEN_14B,
    # ModelType.MISTRAL_24B,
    # ModelType.DEEPSEEK_LLAMA_70B,
]

for model in models:
    print(f'----------------------- RUNNING EXPERIMENTS FOR MODEL: {model} ----------------------')
    main(model=model, output_file=f"results_{model}.json")
    logger.reset()