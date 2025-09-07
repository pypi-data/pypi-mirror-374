from setuptools import setup, find_packages

setup(
    name="signals_ICT_Tejas_Vadgama_92510133044",   # Package name
    version="1.0.0",                                # Version
    packages=find_packages(where="src"),            # Look for modules in src/
    package_dir={"": "src"},                        # src is the root
    install_requires=[
        "numpy",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": [
            "run-signals=main:main",  # optional CLI, requires main.py to have a main() function
        ],
    },
    author="Tejas Vadgama K.",
    description="Signal processing project: unitary signals, trigonometric signals, and basic operations.",
    url="https://github.com/yourusername/signals_ICT_Tejas_Vadgama_92510133044",  # optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
