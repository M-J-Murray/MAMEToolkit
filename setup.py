import shutil
import os

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py


class build(build_py):

    def run(self):
        build_py.run(self)
        binary_file = os.path.join('binary', 'mame')
        if os.path.exists(binary_file):
            dest_dir = os.path.join(self.build_lib, 'emulator', 'mame')
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)
            shutil.copy(binary_file, dest_dir)


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="MAMEToolkit",
    version="1.0.3",
    author="Michael Murray",
    author_email="m.j.murray123@gmail.com",
    description="A library to train your RL algorithms against MAME arcade games on Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/M-J-Murray/MAMEToolkit",
    zip_safe=False,
    packages=find_packages("MAMEToolkit", exclude=['MAMEToolkit/emulator/mame/roms']),
    package_dir={"": "MAMEToolkit"},
    include_package_data=True,
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
