"""Dataset-specific automatic labeling settings (no credentials)."""

import json
import os
import tempfile
from pathlib import Path

import yaml


CONFIG_FILENAME = "ppocrlabel.json"
MODEL_PRESETS = (
    "PP-OCRv5_mobile",
    "PP-OCRv5_server",
    "PP-OCRv6_tiny",
    "PP-OCRv6_small",
    "PP-OCRv6_medium",
)
LANGUAGES = {
    "ch": "Chinese & English",
    "en": "English",
    "french": "French",
    "german": "German",
    "korean": "Korean",
    "japan": "Japanese",
}


def default_config(language="ch"):
    return {
        "model_source": "official",
        "preset": MODEL_PRESETS[0],
        "language": language if language in LANGUAGES else "ch",
        "det_model_dir": "",
        "rec_model_dir": "",
    }


def validate_config(value, language="ch"):
    if not isinstance(value, dict) or value.get("schema_version", 1) != 1:
        raise ValueError("Unsupported ppocrlabel.json format")
    config = default_config(language)
    for key in config:
        if key in value:
            if not isinstance(value[key], str):
                raise ValueError("Invalid setting: " + key)
            config[key] = value[key]
    if config["model_source"] not in ("official", "local"):
        raise ValueError("Invalid model source")
    if config["preset"] not in MODEL_PRESETS:
        raise ValueError("Invalid model preset")
    if config["language"] not in LANGUAGES:
        raise ValueError("Invalid model language")
    return config


def load_config(directory, language="ch"):
    path = Path(directory) / CONFIG_FILENAME
    if not path.exists():
        return default_config(language)
    with path.open(encoding="utf-8-sig") as stream:
        return validate_config(json.load(stream), language)


def save_config(directory, config):
    # Whitelist fields so credentials can never enter a shared dataset.
    value = {"schema_version": 1, **validate_config(config)}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=directory, delete=False
        ) as stream:
            temporary = stream.name
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, Path(directory) / CONFIG_FILENAME)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def local_model_name(directory):
    path = Path(directory).expanduser().resolve()
    if not (path / "inference.pdiparams").is_file() or not any(
        (path / name).is_file() for name in ("inference.json", "inference.pdmodel")
    ):
        raise ValueError("Select a Paddle inference model directory: " + str(path))
    with (path / "inference.yml").open(encoding="utf-8-sig") as stream:
        config = yaml.safe_load(stream)
    name = (
        config.get("Global", {}).get("model_name") if isinstance(config, dict) else None
    )
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Missing Global.model_name in " + str(path / "inference.yml"))
    return name, str(path)


def resolve_models(config, overrides=None):
    config = validate_config(config)
    options = {
        "det_model_name": config["preset"] + "_det",
        "rec_model_name": config["preset"] + "_rec",
        "det_model_dir": None,
        "rec_model_dir": None,
    }
    if config["model_source"] == "local":
        options.update(
            det_model_dir=config["det_model_dir"],
            rec_model_dir=config["rec_model_dir"],
        )
    overrides = overrides or {}
    options.update(
        {k: v for k, v in overrides.items() if k in options and v is not None}
    )
    for task in ("det", "rec"):
        directory_key, name_key = task + "_model_dir", task + "_model_name"
        directory = options[directory_key]
        if directory is None:
            continue
        if not directory.strip():
            raise ValueError("Select the " + task + " inference model directory")
        name, path = local_model_name(directory)
        if name_key in overrides and overrides[name_key] != name:
            raise ValueError("Model name does not match inference.yml: " + name)
        options[name_key], options[directory_key] = name, path
    return options
