from setuptools import setup

# TODO: add setup_requires to the setup()
# [options] setup_requires = wheel >= 0.37.1 setuptools >= 44.0.0


setup(
    name="syve",
    version="0.1",
    py_modules=["main"],
    setup_requires=[
        "wheel>=0.37.1",
        "setuptools>=44.0.0",
    ],
    install_requires=[
        "click",
        "requests",
    ],
    entry_points="""
        [console_scripts]
        syve=main:main
    """,
)


# installing the CLI:
# python setup.py sdist; pip install .
# (Install it globally?)
