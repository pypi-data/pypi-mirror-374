from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cutml",
    version="0.1.0",
    description="Comprehensive Unified Traditional Machine Learning with Auto-Explainability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="email@example.com",
    url="https://github.com/yourusername/cutml",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cutml=cutml.cli:main',
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
        "Topic :: Scientific/Engineering :: Information Analysis", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    keywords="machine learning, explainable AI, SHAP, LIME, ELI5, AutoML, traditional ML, model interpretation",
)
