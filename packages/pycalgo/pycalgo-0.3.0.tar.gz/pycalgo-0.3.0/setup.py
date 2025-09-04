from setuptools import setup, find_packages

setup(
    name="pycalgo",
    version="0.3.0",  # Incremented for new features
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "pycalgo": ["*.dll", "*.so", "*.dylib"]  # Include all library types
    },
    description="A cross-platform Python calculator library using Go-based native implementations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pranesh",
    author_email="praneshmadhan646@gmail.com",
    url="https://github.com/Pranesh-2005/Go_plus_python_simple_calculator_package",  # Add your repo URL
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    keywords="calculator, math, go, native, performance, cross-platform",
    python_requires=">=3.6",
)