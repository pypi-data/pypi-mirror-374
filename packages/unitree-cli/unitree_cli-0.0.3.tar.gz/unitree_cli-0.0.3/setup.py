import os
import shutil
from setuptools import setup, find_packages

setup(
    name="unitree_cli",
    version="0.0.3",
    description="Unitree Cli Tools",
    author="Agnel Wang",
    author_email="2273421791wk@gmail.com",
    license="Apache License 2.0",
    packages=find_packages(where=".", include=["unitree_cli*"]),
    install_requires=[
        "rich-click",
        "paramiko",
        "unitree_dds_wrapper>=2.0.7",
    ],
    entry_points={
        "console_scripts": [
            "unitree=unitree_cli.cli.main:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

# add conda activation scripts
# 自动补全仅在conda环境下生效
conda_prefix = os.environ.get("CONDA_PREFIX")
if conda_prefix:
    activate_dir = os.path.join(conda_prefix, "etc", "conda", "activate.d")
    deactivate_dir = os.path.join(conda_prefix, "etc", "conda", "deactivate.d")
    os.makedirs(activate_dir, exist_ok=True)
    os.makedirs(deactivate_dir, exist_ok=True)

    shutil.copy("scripts/unitree_completion.sh", activate_dir)
    shutil.copy("scripts/unitree_decompletion.sh", deactivate_dir)
