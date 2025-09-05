from setuptools import setup, find_packages
from pathlib import Path

long_description = Path("PhiPhaDL/CHANGELOG.md").read_text()

setup(
    name="phiphadl",
    version="0.1.4",
    description="Deep learning training and testing pipelines",
    packages=find_packages(),  # automatically finds PhiPhaDL/
    install_requires=["torch", "numpy", "matplotlib", "seaborn", "scikit-learn"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
