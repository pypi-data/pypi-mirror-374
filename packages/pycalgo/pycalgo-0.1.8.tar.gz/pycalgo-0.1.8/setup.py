from setuptools import setup
import os

# Ensure calculator.dll exists
if not os.path.exists("calculator.dll"):
    print("Warning: calculator.dll not found!")

setup(
    name="pycalgo",
    version="0.1.8",
    py_modules=["pycal"],
    include_package_data=True,
    data_files=[(".", ["calculator.dll"])],  # Install DLL to same directory as module
    description="A Python calculator library using Go-based DLL implementation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pranesh",
    author_email="praneshmadhan646@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)