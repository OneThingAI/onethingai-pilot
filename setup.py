from setuptools import setup, find_packages

setup(
    name="onethingai-pilot",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.26.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.8",
)
