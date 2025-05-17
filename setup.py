from setuptools import setup, find_packages

setup(
    name="mta_train_tracker",
    version="0.1.0",
    description="A Python library for tracking MTA train status and real-time data.",
    author="Matthew Weisberg",
    author_email="youremail@example.com",
    url="https://github.com/Matthew-Weisberg/nycmta-train-tracker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "protobuf>=4.0.0,<5.0.0",
        "requests>=2.26.0,<3.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)