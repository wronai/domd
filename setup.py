from setuptools import find_packages, setup

setup(
    name="domd",
    version="2.2.50",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pyyaml>=6.0",
        "toml>=0.10.2",
        "configparser>=5.3.0",
        "docker>=6.1.3",
        "flask-cors>=6.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-docker>=2.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pylint>=2.17.0",
            "pre-commit>=3.0.0",
            "coverage[toml]>=7.0.0",
            "codecov>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "domd=domd.cli:main",
            "domd-api=domd.api:main",
            "project-detector=domd.cli:main",
            "cmd-detector=domd.cli:main",
        ],
    },
    python_requires=">=3.9,<4.0",
)
