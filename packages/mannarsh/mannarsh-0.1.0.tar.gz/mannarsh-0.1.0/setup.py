from setuptools import setup, find_packages

setup(
    name='mannarsh',               # Your package name (must be unique on PyPI)
    version='0.1.0',               # Initial version
    description='A simple package providing multiplication tables up to 10',
    author='Mannarsh Singh Bali',  # Your name
    packages=find_packages(),      # Automatically find sub-packages
    install_requires=[             # Dependencies (leave empty if none)
        # Example: 'numpy>=1.21.0'
    ],
    python_requires=">=3.8",       # Minimum Python version
)