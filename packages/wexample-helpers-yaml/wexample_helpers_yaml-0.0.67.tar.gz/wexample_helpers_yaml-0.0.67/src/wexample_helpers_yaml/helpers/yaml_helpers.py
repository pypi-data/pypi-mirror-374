from __future__ import annotations

import yaml
from wexample_helpers_yaml.const.types import YamlContent, YamlContentDict


def yaml_read(file_path: str, default: YamlContent | None = None) -> YamlContent | None:
    try:
        with open(file_path) as f:
            content = yaml.safe_load(f)

            if isinstance(content, dict):
                return content
            else:
                return default
    except Exception:
        return default


def yaml_read_dict(
    file_path: str, default: YamlContentDict | None = None
) -> YamlContentDict:
    content = yaml_read(file_path, default)

    if not content:
        return default or {}

    assert isinstance(content, dict)

    return content


def yaml_write(file_path: str, content: YamlContent) -> None:
    with open(file_path, "w") as f:
        yaml.safe_dump(content, f)
