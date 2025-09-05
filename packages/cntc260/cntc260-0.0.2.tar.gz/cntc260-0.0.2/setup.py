from setuptools import setup
setup(
    name='cntc260',
    version='0.0.2',
    packages=['cntc260'],
    url='https://github.com/OPN48/cntc260',
    author='cuba3',
    author_email='cuba3@163.com',
    long_description=open('README.rst', encoding='utf-8').read(),
)

# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*
#