import shutil
import os

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from distutils.dir_util import copy_tree


def copy_to_build(file_path, build_dir):
    if os.path.exists(file_path):
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)
        if os.path.isdir(file_path):
            copy_tree(file_path, build_dir)
        else:
            shutil.copy(file_path, build_dir)


class build(build_py):

    def run(self):
        build_py.run(self)
        copy_to_build("binary/mame", os.path.join(self.build_lib, 'MAMEToolkit/emulator/mame'))
        copy_to_build("src/MAMEToolkit/emulator/mame/fonts", os.path.join(self.build_lib, 'MAMEToolkit/emulator/mame/fonts'))
        copy_to_build("src/MAMEToolkit/emulator/mame/plugins", os.path.join(self.build_lib, 'MAMEToolkit/emulator/mame/plugins'))
        copy_to_build("src/MAMEToolkit/.libs", os.path.join(self.build_lib, 'MAMEToolkit/.libs'))


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="MAMEToolkit",
    version="1.1.0",
    author="Michael Murray",
    author_email="m.j.murray123@gmail.com",
    description="A library to train your RL algorithms against MAME arcade games on Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/M-J-Murray/MAMEToolkit",
    zip_safe=False,
    packages=find_packages("src", exclude=["src/MAMEToolkit/.libs", "src/MAMEToolkit/emulator/mame"]),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux"
    ],
    install_requires=[
        'numpy',
    ],
    cmdclass={
        'build_py': build,
    }
)
