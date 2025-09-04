from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kumir",
    version="0.1.1",
    author="arli",
    author_email="volodya.artemev.1999@mail.ru",
    description="test package for kumir",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vovmomyt/kumir",
    packages=["kumir"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Укажите зависимости вашего пакета, например:
        # "numpy>=1.18.0",
        # "pandas>=1.0.0",
    ],
)
