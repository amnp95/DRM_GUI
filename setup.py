from setuptools import setup, find_packages

setup(
    name="drm_analyzer",
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
            "drm-analyzer=drm_analyzer.main:main",
        ],
    },
)