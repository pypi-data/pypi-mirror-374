import inspect
from pathlib import Path
from typing import Any, Callable


def path_to_module_name(path: Path) -> str:
    """
    转换路径为模块名
    Args:
        path: 路径a/b/c/d -> a.b.c.d
    Returns:
        str: 模块名
    """
    rel_path = path.resolve().relative_to(Path.cwd().resolve())
    if rel_path.stem == "__init__":
        return ".".join(rel_path.parts[:-1])
    else:
        return ".".join(rel_path.parts[:-1] + (rel_path.stem,))


def parse_function_docsring():
    pass
