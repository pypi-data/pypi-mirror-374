from setuptools import setup, find_packages

setup(
    name="unicore",                # unique PyPI name
    version="2",             # bump this every upload
    description="version 2.0.0",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Soly147",
    author_email="",
    url="",  # optional
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.1",
    install_requires=[   # dependencies if any
        # "requests>=2.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
