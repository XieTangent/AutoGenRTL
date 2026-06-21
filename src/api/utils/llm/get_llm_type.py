MODEL_FORMATS = {
    "openai": [
        "gpt-4", "o1-mini", "gpt-4o-mini", "gpt-4o",
        "gpt-3.5-turbo", "o3-mini", "o1"
    ],
    "grok": [
        "grok-3-mini-beta"
    ],
}

def get_model_type(model_name):
    for model_type, models in MODEL_FORMATS.items():
        if model_name in models:
            return model_type
    return None
