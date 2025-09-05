from setuptools import setup, find_packages
import glob
setup(
    name="JooFunc",
    version="1.0.0",
    packages=find_packages(),
    scripts=glob.glob('JooFunc/*.py')
)
