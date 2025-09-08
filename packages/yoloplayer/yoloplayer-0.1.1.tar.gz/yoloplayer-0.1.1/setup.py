from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="yoloplayer",
    version="0.1.1",  
    description="An OpenCV video player wrapper with YOLO detection support",
    long_description=long_description,  
    long_description_content_type="text/markdown",  
    author="Raunit Singh",
    author_email="raunitsingh33@email.com",
    url="https://github.com/raunitsingh/yoloplayer",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.0",
        "ultralytics>=8.0.0",
        "numpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
