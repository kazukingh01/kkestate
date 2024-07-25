from setuptools import setup, find_packages

packages = find_packages(
        where='.',
        include=['kkestate*']
)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='kkestate',
    version='1.1.0',
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
        'kkpsgre @ git+https://github.com/kazukingh01/kkpsgre.git@8ebc13408318c33c1bd7ae80e778c80ce67c9832',
        'pandas==2.2.1',
        'numpy==1.26.4',
        'requests==2.32.3',
        'beautifulsoup4==4.12.3',
        'joblib==1.3.2',
    ],
    python_requires='>=3.12.2'
)
