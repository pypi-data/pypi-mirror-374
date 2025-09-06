from setuptools import setup, find_packages

setup(
    name='hashvault',
    version='0.1.2',
    description='User authentication module with password hashing',
    author='Loïc LOKOSSOU',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.6',
)