from setuptools import setup, find_packages

setup(
    name="dfcleanan",  
    version="0.1.4",
    author="Ozodbek_Qurbonov",
    description="DataFrame clean nan data",
    packages=find_packages(),
    install_requires=["pandas>=2.0.0"],
    python_requires=">=3.13",
    license="MIT",
)
