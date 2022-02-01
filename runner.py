import os
import subprocess
from time import sleep

import script_writer
import config


def create_mesh(
    lattice_structure,
    channel_spacing,
    channel_width,
    channel_height,
):
    mesh_structure_string = "-".join(
        str(layer) for layer in lattice_structure
    )

    save_name = os.path.join(
        config.MESH_PATH,
        f"{mesh_structure_string}"
        f"_{channel_spacing}"
        f"_{channel_width}"
        f"_{channel_height}"
        f".unv",
    )
    mesh_variables = dict(
        path_name=f'r"{config.PATH_NAME}"',
        lattice_structure=lattice_structure,
        channel_spacing=channel_spacing,
        channel_width=channel_width,
        channel_height=channel_height,
        save_name=f'r"{save_name}"',
    )
    script_writer.write_script(
        template_path=os.path.join(
            config.TEMPLATE_PATH, "salome_script.py.template"
        ),
        variables=mesh_variables,
        temp_dir_path=config.TEMP_DIR_PATH,
    )
    subprocess.run(
        [r"run_salome.bat", "-t", "tmp/script.py"],
    )
    while not os.path.exists(save_name):
        sleep(1)

    script_writer.delete_script(config.TEMP_DIR_PATH)
