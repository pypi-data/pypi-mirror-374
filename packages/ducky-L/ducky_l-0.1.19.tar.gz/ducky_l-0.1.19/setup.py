from setuptools import setup, find_packages

setup(
    name="ducky_L",  # el nombre en PyPI
    version="0.1.19",  # cambia cada vez que subas actualización
    author="José Pato",
    author_email="patodequeso222@gmail.com",
    description="Un lenguaje pato creado por José Pato 🦆",
    long_description=open("README.md", encoding="utf-8").read(),  # si tienes README
    long_description_content_type="text/markdown",
    packages=find_packages(),  # busca todos los paquetes Python
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "fastapi",
        "uvicorn"
    ],
    python_requires=">=3.7",
)
