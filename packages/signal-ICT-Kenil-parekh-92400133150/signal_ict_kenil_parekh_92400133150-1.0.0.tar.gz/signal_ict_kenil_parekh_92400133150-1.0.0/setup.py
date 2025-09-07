from setuptools import setup, find_packages

setup(
    name="signal_ICT_Kenil_parekh_92400133150",  # your package name
    version="1.0.0",
    packages=find_packages(),                    # automatically find your package
    install_requires=[                           # optional dependencies
        "numpy",
        "matplotlib"
    ],
    author  ="Kenil parekh",
    description="Python package for signal processing exercises",
    python_requires=">=3.6"
)
