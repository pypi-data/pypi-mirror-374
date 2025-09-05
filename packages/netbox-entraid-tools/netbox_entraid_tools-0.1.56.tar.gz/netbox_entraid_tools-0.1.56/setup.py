from setuptools import setup, find_packages
from pathlib import Path
import ast

META_VARS = {"__version__", "__author__", "__author_email__", "__description__", "__project_url__"}


def read_meta(package_init: Path):
    text = package_init.read_text(encoding="utf-8")
    tree = ast.parse(text)
    meta = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id in META_VARS:
                    val = node.value
                    if isinstance(val, ast.Constant) and isinstance(val.value, str):
                        meta[tgt.id] = val.value
    missing = META_VARS - set(meta)
    if missing:
        raise RuntimeError(f"Missing metadata in {package_init}: {sorted(missing)}")
    return meta


meta = read_meta(Path("netbox_entraid_tools/__init__.py"))


with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="netbox-entraid-tools",
    version=meta["__version__"],
    author=meta["__author__"],
    author_email=meta["__author_email__"],
    description=meta["__description__"],
    url=meta["__project_url__"],
    project_urls={
        "Bug Tracker": meta["__project_url__"] + "/issues",
        "Source Code": meta["__project_url__"],
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "netbox_plugins": [
            "netbox_entraid_tools = netbox_entraid_tools",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Framework :: Django",
    ],
    # Explicitly declare package data for templates/static
    package_data={
        "netbox_entraid_tools": [
            "templates/netbox_entraid_tools/*.html",
            "static/netbox_entraid_tools/*",
        ],
    },
)
