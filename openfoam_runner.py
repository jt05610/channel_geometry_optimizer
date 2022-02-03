import os
import platform
import sys
import subprocess

if __name__ == "__main__":
    home = os.environ["HOME"]
    foam_home = os.path.join(home, "OpenFOAM")
    mesh = "meshes/2-1-2-3-2-1-2-3-2-1-1_5_0.5_0.56.unv"
    run_script = "./foam_run/lockExchange-base/Allrun"
    os.system("touch /home/jtaylor/test.file")
    print(home)
    a = input("did it work?")
