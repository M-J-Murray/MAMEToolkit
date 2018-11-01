from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="MAMEToolkit",
    version="1.0.0",
    author="Michael Murray",
    author_email="m.j.murray123@gmail.com",
    description="A library to train your RL algorithms against MAME arcade games on Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/M-J-Murray/MAMEToolkit",
    packages=find_packages(exclude=['MAMEToolkit/emulator/mame/roms']),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux"
    ],
)