from setuptools import setup, find_packages

setup(
    name="Palima",
    version="0.0.0.1",
    packages=find_packages(),
    requires=[],
    entry_points={
        "console_scripts":[
            "Palima --info = nfu:nfuoft"
        ]
    }
)
