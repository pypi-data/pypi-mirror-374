from setuptools import setup, find_packages

setup(
    name="dfcleanan",  
    version="0.1.5",  # versiyani oshirish shart (PyPI’da eski versiyani qayta yuklab bo‘lmaydi)
    author="Ozodbek Qurbonov",
    author_email="qurbonovo2008@gmail.com",  # xohlasang yoz, xohlamasang bo‘sh qoldir
    description="A Python package to clean NaN values in pandas DataFrames",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/QurbonovAI",  # agar GitHub bo‘lsa qo‘y
    license="MIT",
    packages=find_packages(include=["dfcleanan", "dfcleanan.*"]),
    install_requires=[
        "pandas>=2.3.2",
    ],
    python_requires=">=3.8",  # faqat 3.13 emas, kengroq qo‘ygan yaxshiroq
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
