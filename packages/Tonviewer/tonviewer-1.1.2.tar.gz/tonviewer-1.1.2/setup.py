import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    lng_description = fh.read()

setuptools.setup(
    name="Tonviewer",
    version="1.1.2",
    author="deep",
    author_email="asyncpy@proton.me",
    license="MIT",
    description="TON Crypto Info Scraper is a Python library that allows you to fetch ( real-time balance of wallet , transactions , price ) data without needing any APIs.",
    long_description=lng_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "Tonviewer=Tonviewer.cil:console",
        ],
    },
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
