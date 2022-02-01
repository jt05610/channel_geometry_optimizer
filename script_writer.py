import os
from typing import Tuple, Iterable


def get_template(template_path: str) -> list:
    with open(template_path, "r") as f:
        return f.readlines()


def parse_template_vars(template: list) -> Iterable[Tuple[int, str]]:
    for i, line in enumerate(template):
        if line.lstrip(" ")[0] == "$":
            yield i, line


def replace_template_vars(template_path: str, variables: dict):
    template = get_template(template_path)
    for i, line in parse_template_vars(template):
        split_line = line.split("$")
        var_name = split_line[-1].strip(",\n")
        indent = split_line[0]
        new_line = f"{indent}{variables[var_name]},\n"
        template[i] = new_line
    return template


def write_script(template_path: str, variables: dict, temp_dir_path: str):
    modified_template = replace_template_vars(template_path, variables)
    with open(os.path.join(temp_dir_path, "script.py"), "w") as f:
        f.writelines(modified_template)
    return variables["save_name"]


def delete_script(temp_dir_path: str):
    try:
        os.remove(os.path.join(temp_dir_path, "script.py"))
    except FileNotFoundError:
        pass
