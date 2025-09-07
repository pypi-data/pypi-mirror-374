from setuptools import setup, find_packages

setup(
    name="osmomemo",
    version="1.0.0",

    author="osmiumnet",
    description="Python omemo package",

    packages=find_packages(),
    install_requires=[
        "cryptography>=45.0.6",
        "pynacl>=1.5.0",
        "sqlalchemy>=2.0.43",
    ],
    python_requires=">=3.10",
)
