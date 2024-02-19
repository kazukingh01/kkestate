from setuptools import setup, find_packages

packages = find_packages(
        where='.',
        include=['kkestate*']
)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='kkestate',
    version='1.0.0',
    description="Collecting real estate data for using it parsonaly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kazukingh01/kkestate",
    author='kazukingh01',
    author_email='kazukingh01@gmail.com',
    license='Private License',
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Private License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'kkpsgre @ git+https://github.com/kazukingh01/kkpsgre.git@894ef961d66aff7355bb839d0e6a2156e14ff8eb',
        'pandas==1.5.3',
        'numpy==1.24.2',
        'requests==2.28.2',
        'beautifulsoup4==4.12.3',
    ],
    python_requires='>=3.11.2'
)
