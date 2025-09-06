from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantum-docker-engine",
    version="1.0.2",
    description="Revolutionary container orchestration engine powered by quantum computing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Quantum Docker Team",
    author_email="contact@quantumdocker.io",
    url="https://github.com/quantum-docker/engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="quantum computing, container orchestration, docker, kubernetes, quantum algorithms",
    install_requires=[
        "cirq>=1.3.0,<1.7.0",
        "numpy>=1.21.0,<2.0.0",
        "docker>=6.1.3",
        "click>=8.1.7",
        "pyyaml>=6.0.1",
        "rich>=13.7.0",
        "typing-extensions>=4.8.0",
        "matplotlib>=3.7.2",
        "scipy>=1.11.0,<2.0.0",
        "networkx>=3.1,<4.0.0",
        "psutil>=5.9.5",
        "protobuf>=5.26,<6.0",
        "attrs>=23.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "pytest-asyncio>=0.21.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "qiskit": [
            "qiskit>=0.45.0,<3.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "qdocker=quantum_docker.cli.cli:main",
        ],
    },
    python_requires=">=3.8",
    zip_safe=False,
    include_package_data=True,
    package_data={
        "quantum_docker": ["*.yaml", "*.yml", "*.json"],
    },
)
