import os
import shutil
from collections import namedtuple
from math import sin, cos, radians
from enum import Enum
from typing import List, Iterator, Union, Iterable
from config import TEMPLATE_PATH, CASES_PATH


class OpenFoamObject(str, Enum):
    U = "U"
    P_RGH = "p_rgh"
    ALPHA = "alpha.organic.orig"
    TRANSPORT_PROPERTIES = "transportProperties"
    SET_FIELDS_DICT = "setFieldsDict"

    def __str__(self):
        return str.__str__(self)


Velocity = namedtuple(
    typename="Velocity",
    field_names=("x", "y", "z"),
)


TemplateComponent = namedtuple(
    typename="TemplateComponent", field_names=("component_name", "lines")
)


ExperimentVariable = namedtuple(
    typename="ExperimentVariable", field_names=("type", "name", "fields")
)

BoundingBox = namedtuple(
    typename="BoundingBox",
    field_names=(
        "x1",
        "y1",
        "z1",
        "y2",
        "x2",
        "z2",
    ),
)


VariableFields = namedtuple(
    typename="VariableFields",
    field_names=("U", "alpha", "p_rgh", "field_box", "nu", "rho"),
)

ChannelVelocity = namedtuple(
    typename="ChannelVelocity",
    field_names=("flow_rate", "height", "width", "channel_angle"),
)


Case = namedtuple(
    typename="Case", field_names=("case_name", "solver", "variables")
)


def indent_lines(lines: List[str]):
    return list(map(lambda x: "    " + x, lines))


def foam_string(item: Union[BoundingBox, Velocity]) -> str:
    match type(item).__name__:
        case "BoundingBox":
            ret = f"box ({item.x1} {item.y1} {item.z1}) ({item.x2} {item.y2} {item.z2})"
        case "Velocity":
            ret = f'uniform ({" ".join(str(v) for v in item)})'
        case _:
            ret = None
    return ret


def calculate_velocity(
    flow_rate: float, height: float, width: float, channel_angle: float
):
    cubic_millimeters_per_second = flow_rate * 1000 / 60
    cross_section_area = height * width
    velocity_millimeters_per_second = (
        cubic_millimeters_per_second / cross_section_area
    )
    velocity_meters_per_second = velocity_millimeters_per_second / 1000
    return Velocity(
        x=round(cos(radians(channel_angle)) * velocity_meters_per_second, 4),
        y=round(sin(radians(channel_angle)) * velocity_meters_per_second, 4),
        z=0,
    )


def get_template(obj: Union[str, OpenFoamObject]) -> List[str]:
    template_file = os.path.join(TEMPLATE_PATH, f"{obj}.template")
    with open(template_file, "r") as f:
        return f.readlines()


def parse_component(lines: List[str], name: str):
    ret = None
    start = lines.index(name)
    for i, line in enumerate(lines[start:]):
        if line == "}\n":
            ret = lines[start:start + i + 1]
            break
    return ret


def parse_template_components(
    obj: Union[str, OpenFoamObject]
) -> Iterator[TemplateComponent]:
    template_component_file = os.path.join(
        TEMPLATE_PATH, f"{obj}_components.template"
    )
    with open(template_component_file, "r") as f:
        lines = f.readlines()
    component_names = filter(lambda line: line[0] == "$", lines)
    for component in component_names:
        yield TemplateComponent(
            component.strip("\n"), parse_component(lines, component)
        )


def parse_component_variables(component: TemplateComponent) -> Iterator[str]:
    for line in component.lines[1:]:
        if "$" in line:
            split_line = line.split(" ")
            has_variables = filter(lambda word: len(word) > 0, split_line)
            variable_name = next(
                filter(lambda word: word[0] == "$", has_variables)
            )
            yield variable_name[1:].split(";")[0]


def replace_variable(
    obj: OpenFoamObject,
    component: TemplateComponent,
    experiment_variable: ExperimentVariable,
):
    if "." in str(obj):
        obj = str(obj).split(".")[0]
    try:
        value = getattr(experiment_variable.fields, obj)
    except AttributeError:
        value = None
    match type(value).__name__:
        case "ChannelVelocity":
            value = foam_string(calculate_velocity(*value))
        case _:
            value = str(value)

    try:
        if obj == "transportProperties" and experiment_variable.name.split(
            "_"
        )[0] in ("organic", "aqueous"):
            variables = parse_component_variables(component)
            values = dict(
                map(
                    lambda v: (v, getattr(experiment_variable.fields, v)),
                    variables,
                )
            )
            for i, line in enumerate(component.lines):
                if i == 0:
                    line = line.replace(
                        "$fluid", experiment_variable.name.split("_")[0]
                    )
                if "$" in line:
                    variable = line.split("$")[-1].split(";")[0]
                    line = line.replace(f"${variable}", str(values[variable]))
                yield line
        else:
            variable = next(parse_component_variables(component))

            for i, line in enumerate(component.lines):
                if i == 0:
                    line = line.replace(
                        f"{experiment_variable.type}_{obj}",
                        experiment_variable.name,
                    )
                if "$" in line:
                    line = line.replace(
                        f"${variable}",
                        value,
                    )
                yield line
    except StopIteration:
        for i, line in enumerate(component.lines):
            if i == 0:
                line = line.replace(
                    f"{experiment_variable.type}_{obj}",
                    experiment_variable.name,
                )
            yield line


def insert_experiment_variable(
    obj: Union[str, OpenFoamObject], experiment_variable: ExperimentVariable
):
    components = parse_template_components(obj)
    obj = obj.split(".")[0] if "." in obj else obj
    try:
        component_to_insert = next(
            filter(
                lambda x: x.component_name
                == f"{experiment_variable.type}_{obj}",
                components,
            )
        )
        lines = list(
            replace_variable(obj, component_to_insert, experiment_variable)
        )
    except StopIteration:
        if obj == "transportProperties":
            component_to_insert = next(parse_template_components(obj))
            lines = list(
                replace_variable(obj, component_to_insert, experiment_variable)
            )
        else:
            lines = []
    return TemplateComponent(
        component_name=None,
        lines=lines,
    )


def get_component_start(template: List[str]) -> int:
    for i, l in enumerate(template):
        if "$components" in l:
            return i


def combine_lines(components: Iterable[TemplateComponent]):
    ret = []
    for c in components:
        if c.lines[0] not in ret and c.lines[0][0] != "$":
            ret += c.lines
    return ret


def replace_variables(
    obj: Union[str, OpenFoamObject], variables: Iterable[ExperimentVariable]
):
    template = get_template(obj)
    start = get_component_start(template)
    template.pop(start)
    if obj == OpenFoamObject.SET_FIELDS_DICT:
        for v in variables:
            if v.fields.field_box is not None:
                template.insert(
                    start, f"        {foam_string(v.fields.field_box)};"
                )
    else:
        components = (insert_experiment_variable(obj, v) for v in variables)
        component_lines = combine_lines(components)
        if obj != OpenFoamObject.TRANSPORT_PROPERTIES:
            component_lines = indent_lines(component_lines)
        for i, l in enumerate(component_lines):
            template.insert(start + i, l)
    return template


def iter_dir(path: str):
    for d in os.listdir(path):
        try:
            yield from iter_dir(os.path.join(path, d))
        except NotADirectoryError:
            yield os.path.join(path, d)


def create_case(case: Case, overwrite: bool = False):
    case_path = os.path.join(CASES_PATH, case.case_name)
    try:
        shutil.copytree(os.path.join(TEMPLATE_PATH, case.solver), case_path)
        objects = filter(
            lambda file: file.split("/")[-1] in tuple(OpenFoamObject),
            iter_dir(case_path),
        )
        for o in objects:
            object_name = o.split("/")[-1]
            lines = replace_variables(object_name, case.variables)
            with open(o, "w") as f:
                f.writelines(lines)

    except FileExistsError:
        if overwrite:
            shutil.rmtree(case_path)
            create_case(case)
        else:
            return
