from setuptools import setup, find_packages

setup(
    name="prabhatai",
    version="0.1.0",
    description="Thin wrapper for OpenRouter chat completions API",
    author="Prabhat Kumar",
    license="MIT",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7",
    include_package_data=True,
)
