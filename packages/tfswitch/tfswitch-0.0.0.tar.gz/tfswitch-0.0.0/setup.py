from setuptools import setup, find_packages

setup(
    name="tfswitch",
    author="Chowdhury Faizal Ahammed",
    description="Python CLI Utility to switch between various versions of Terraform seamlessly",
    packages=find_packages(),
    install_requires=[
        "requests",
        "InquirerPy",
        "packaging",
        "urllib3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "tfswitch=tfswitch.cli:main",
        ],
    },
    python_requires=">=3.7",
)
