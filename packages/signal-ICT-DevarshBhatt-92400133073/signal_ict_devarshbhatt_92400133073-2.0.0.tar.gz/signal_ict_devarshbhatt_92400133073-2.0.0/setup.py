from setuptools import setup, find_packages

setup(
    name="signal_ICT_DevarshBhatt_92400133073",
    version="2.0.0",
    author="DEVARSH BHATT",
    author_email="devarsh.bhatt128171@marwadiuniversity.ac.in",
    description="Python package for signal generation and operations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib"
    ],
    license="MIT",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)