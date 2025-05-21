from const import ModelType
from baseline_agent import main

models = [
    ModelType.QWEN_0_5B,
    ModelType.DEEPSEEK_1_5B,
    ModelType.QWEN_7B,
    ModelType.DEEPSEEK_QWEN_14B,
    ModelType.MISTRAL_24B,
    ModelType.LLAMA_3_3_70B,
]

for model in models:
    main(model=model, output_file=f"results_{model}.json")