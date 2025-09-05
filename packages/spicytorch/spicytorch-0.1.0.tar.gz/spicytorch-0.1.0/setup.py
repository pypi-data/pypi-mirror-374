from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="spicytorch",
    version="0.1.0",
    description="🌶️ Advanced PyTorch Components from Latest Research Papers - Spicing up your models!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="email@example.com",
    url="https://github.com/yourusername/spicytorch",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'spicytorch=spicytorch.cli:main',
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="pytorch, deep learning, activation functions, loss functions, optimizers, augmentation, research papers, neural networks",
)
