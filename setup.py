from setuptools import setup

with open("README", 'r') as f:
    long_description = f.read()

with open("requirements.txt", 'r') as f:
    requirements = [s.split("==")[0] for s in f.read().split('\n') if len(s)]

setup(
   name='yaam',
   version='0.0.0.1',
   description='Yet Another Addon Manager',
   license="GPL-3.0",
   long_description=long_description,
   author='Alessandro Cevoli',
   author_email='bibo.cevoli@gmail.com',
   url="https://github.com/XanderC94/YAAM",
   packages=['yaam'],  #same as name
   install_requires=requirements, #external packages as dependencies
   scripts=[]
)
