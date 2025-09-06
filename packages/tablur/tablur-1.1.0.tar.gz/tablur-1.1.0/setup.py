from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tablur",
    version="1.1.0",
    author="Duro",
    author_email="davidwright13503@gmail.com",
    description="a simple callable library for creating formatted tables with box-drawing characters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/durocodes/tablur",
    project_urls={
        "Bug Reports": "https://github.com/durocodes/tablur/issues",
        "Source": "https://github.com/durocodes/tablur",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    keywords="table formatting ascii box-drawing terminal callable",
    include_package_data=True,
)
