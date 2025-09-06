from distutils.core import setup

def calc_git_version():
    import subprocess
    import os
    try:
        version = subprocess.run(['git', 'describe', '--tags', '--broken', '--dirty'], check=True, capture_output=True, encoding='utf-8').stdout
        assert version[0] == "v"
        version = version.strip().removeprefix("v")
        version = version.replace("-broken", "+broken")
        version = version.replace("-dirty", "+dirty")
        version = version.replace("-g", "+g")
        version = version.replace("-",".post",1)
    except subprocess.CalledProcessError as e:
        version = os.path.basename(os.path.dirname(__file__)).split("-", maxsplit=1)[1]
    return version

setup(
    name="gdbstub",
    description="Python type stubs for GDB's internal `_gdb` package.",
    long_description=open("README.md","r").read(),
    url="https://github.com/AJMansfield/gdbstub",
    author="Anson Mansfield",
    author_email="amansfield@mantaro.com",
    version=calc_git_version(),
    package_data={"_gdb": ['__init__.pyi']},
    packages=["_gdb"],
    license="GPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Debuggers",
        "Typing :: Stubs Only",
    ],
)