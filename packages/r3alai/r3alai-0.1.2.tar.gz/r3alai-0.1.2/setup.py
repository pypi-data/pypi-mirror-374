from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="r3alai",
    version="0.1.2",
    description="A Python library for Random Set Neural Networks with uncertainty estimation",
    author="Arshia",
    author_email="arshia@r3al.ai",
    packages=find_packages(),  # This will find the r3alai directory and all its subdirectories
    install_requires=[
        "torch>=1.12.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "yolo": ["ultralytics>=8.1.0"],
        "vision": ["torchvision>=0.13.0", "Pillow>=9.0.0"],
        "dev": ["pytest", "build"],
    },
    python_requires=">=3.8",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/R3AL-AI/package",
    project_urls={
        "Bug Tracker": "https://github.com/R3AL-AI/package/issues",
        "Documentation": "https://github.com/R3AL-AI/package#readme",
        "Source Code": "https://github.com/R3AL-AI/package",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)