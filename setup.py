from setuptools import setup, find_packages

NAME = "pyairflow"
VERSION = "0.1.0"

REQUIRES = [
    'pyconfig<1'
]

DEPENDENCY_LINKS = [
    'https://github.com/dohernandez/py-config/tarball/master#egg=pyconfig-0.1.0'
]

setup(
    name=NAME,
    version=VERSION,
    description="Package to manipulate Airflow DAGs for Spark, Impala and Hive operators",
    author_email="dohernandez@gmail.com",
    keywords=["python", "Airflow DAGs"],
    install_requires=REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    packages=find_packages()
)
