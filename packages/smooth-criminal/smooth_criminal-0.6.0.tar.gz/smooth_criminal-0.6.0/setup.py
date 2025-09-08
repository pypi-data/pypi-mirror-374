from setuptools import setup, find_packages

setup(
    name="smooth_criminal",
    version="0.6.0",
    author="Adolfo González",
    author_email="tucorreo@example.com",
    description="Dashboard de análisis de rendimiento con decoradores inteligentes",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Alphonsus411/smooth_criminal",  # Cambiar si aplica
    project_urls={
        "Documentación": "https://smooth-criminal.readthedocs.io/en/latest/",
        "Código fuente": "https://github.com/Alphonsus411/smooth_criminal",
        "Tracker": "https://github.com/Alphonsus411/smooth_criminal/issues",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flet>=0.19.0",
        "pandas",
        "tabulate",
        "matplotlib"
    ],
    extras_require={
        "tinydb": ["tinydb"],
        "sqlite": [],
    },
    entry_points={
        "console_scripts": [
            "smooth-criminal=smooth_criminal.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
