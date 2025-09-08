from setuptools import setup, find_packages

VERSION = "0.0.3"
DESCRIPTION = "ESSL assets management"
LONG_DESCRIPTION = "Internal helper package for ESSL assets management"
setup(
    name="espy_pdfier",
    version="0.26",
    packages=find_packages(),
    install_requires=[
        "reportlab>=4.2.0",
        "pillow>=11.1.0",
        "boto3>=1.36.11",
    ],
    author="Femi Adigun",
    author_email="femi.adigun@myeverlasting.net",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    keywords=["fastapi", "ESSL", "ReachAI"],
)
