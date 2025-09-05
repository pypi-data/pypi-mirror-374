from setuptools import setup, find_packages

setup(
    name="linear_model_Surya_Sudhaharan",
    version="0.1.0",
    description="A lightweight Python library for Linear Regression with multiple training methods and regularization options.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Surya Sudhaharan",
    author_email="surya.sudhaharan@gmail.com",
    url="https://github.com/SuryaVsCode/Linear_Regression_Model",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
)
