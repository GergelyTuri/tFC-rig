from setuptools import find_packages, setup

setup(
    name="cued-fc",
    version="0.1.0",
    description="Codebase to analyze cued fear conditioning experiments",
    author="Gergely, Colin, Austin, Yuecheng",
    author_email="gt2253@cumc.columbia.edu, cmp2250@columbia.edu, as7082@columbia.edu, yuecheng.shi@nyspi.columbia.edu",
    license="MIT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GergelyTuri/tFC-rig",
    packages=find_packages(include=["Analysis", "Analysis.*"]),
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
