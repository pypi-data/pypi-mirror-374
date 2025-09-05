from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="logneuron",
    version="0.1.0",
    description="AI-Powered Log Analysis and Neural Network Intelligence - Coming Soon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="email@example.com",
    url="https://github.com/yourusername/logneuron",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'logneuron=logneuron.cli:main',
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Logging",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="logging, neural networks, AI, log analysis, machine learning, monitoring",
)
