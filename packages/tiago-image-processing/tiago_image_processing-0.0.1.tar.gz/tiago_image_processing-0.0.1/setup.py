from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="tiago-image_processing", #nome do meu pacote
    version="0.0.1", #versão do meu pacote
    author="tiago-image_processing",
    description="Image processing package using Skimage", #descrição do meu pacote
    long_description=page_description, # page_description pega a drescription do README.md
    long_description_content_type="text/markdown",
    url="https://github.com/tiagoosr",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)
