from setuptools import setup, find_packages

setup(
    name="signal_ICT_AumLathigara_92400133189",
    version="2.0.0",
    author="Aum Lathigara",
    author_email="om.lathigara133168@marwadiuniversity.ac.in",
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