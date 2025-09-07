from setuptools import setup, find_packages

setup(
    name="mtcli-volume",
    version="1.0.0",
    description="Plugin mtcli para exibir o volume profile",
    author="Valmir França da Silva",
    author_email="vfranca3@gmail.com",
    packages=find_packages(),
    install_requires=[
        "mtcli>=1.19.4,<2.0.0",
    ],
    entry_points={
        "mtcli.plugins": [
            "mtcli-volume = mtcli_volume.plugin:volume",
        ],
    },
    python_requires='>=3.10,<3.14',
)
