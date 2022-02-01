import subprocess

if __name__ == '__main__':
    subprocess.run(
        [r'run_salome.bat', '-t', 'test_salome_script.py'],
        creationflags=0x00000008,
    )
