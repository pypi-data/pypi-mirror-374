from setuptools import setup, find_packages

setup(
    name="ducky-l",           # Nombre único en PyPI
    version="0.1.0",
    packages=find_packages(include=["ducky", "ducky.*"]),
    install_requires=[],
    author="Jose Poveda",
    author_email="patodequeso222@gmail.com",
    description="Un mini lenguaje en desarrollo",
    long_description=open("README.md").read(),
    long_description_content_type="text",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.10',
)
