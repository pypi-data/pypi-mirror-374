from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="meu_pacote_exemplo",
    version="0.0.1",
    author="Tiago",
    description="Um pacote de exemplo com funções úteis",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tiagoosr/simple-package-template",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)