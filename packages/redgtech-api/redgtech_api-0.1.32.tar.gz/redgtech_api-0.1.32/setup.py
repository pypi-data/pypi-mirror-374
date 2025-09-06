from setuptools import setup, find_packages

setup(
    name="redgtech-api",
    version="0.1.32",
    description="A Python package to interact with the Redgtech API",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/redgtech-automacao/redgtech-python-api",
    author="Jonh Sady",
    author_email="jonh.system@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.7.4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)