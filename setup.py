from setuptools import setup, find_packages

setup(
    name="redaction_system",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'redact=redaction_system.cli.commands:main',
        ],
    },
)
