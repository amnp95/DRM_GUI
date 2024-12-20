from setuptools import setup, find_packages

setup(
    name="meshmaker",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PySide6",
        "pyvista",
        "pyvistaqt",
        "qtconsole",
        "tqdm",
        "h5py"
    ],
    entry_points={
        "console_scripts": [
            "meshmaker=meshmaker.main:main",
        ],
    },
)