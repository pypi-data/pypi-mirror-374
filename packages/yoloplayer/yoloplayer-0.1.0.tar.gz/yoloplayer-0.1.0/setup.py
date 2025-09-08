from setuptools import setup, find_packages

setup(
    name="yoloplayer",
    version="0.1.0",
    description="A wrapper for OpenCV video playback with YOLO detection",
    author="Raunit singh",
    author_email="raunitsingh33@email.com",
    url="https://github.com/raunitsingh/yoloplayer",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "ultralytics"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)