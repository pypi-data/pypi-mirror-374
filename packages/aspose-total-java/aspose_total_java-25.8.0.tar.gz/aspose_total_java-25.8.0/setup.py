from pathlib import Path
from setuptools import setup

NAME = "aspose-total-java"
VERSION = "25.8.0"

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

# Core components (no JPype coupling)
COMMON_REQUIRES = [
    "aspose-cells==25.8.0",
    "aspose-diagram==25.8.0",
    "aspose-ocr-python-java==25.2.0",
    "aspose-pdf-for-python-via-java==24.9",
]

# Extras reflecting JPype constraints (mutually incompatible JPype ranges)
EXTRAS_REQUIRE = {
    # BarCode path needs JPype1==1.4.1
    "barcode": [
        "aspose-barcode-for-python-via-java==25.8.1",
        "JPype1==1.4.1",
    ],

    # Slides path needs JPype1>=1.5.0 (<2.0 to be explicit)
    "slides": [
        "aspose-slides-java==24.6.0",
        "JPype1>=1.5.0,<2.0.0",
    ],

    # Offer *two* full variants so users choose the JPype track explicitly.
    "full-jpype141": [
        # Full + BarCode track (pins JPype to 1.4.1; excludes Slides)
        "aspose-barcode-for-python-via-java==25.8.1",
        "JPype1==1.4.1",
    ],
    "full-jpype15x": [
        # Full + Slides track (allows JPype >=1.5.x; excludes BarCode)
        "aspose-slides-java==24.6.0",
        "JPype1>=1.5.0,<2.0.0",
    ],
}

setup(
    name=NAME,
    version=VERSION,
    description="Aspose.Total for Python via Java: unified meta-package for core Aspose Python-via-Java components.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Aspose",
    author_email="total@aspose.com",
    url="https://products.aspose.com/total/python-java",
    packages=["aspose-total-java"],
    include_package_data=True,

    # Strict pins kept to match release policy
    install_requires=COMMON_REQUIRES,
    extras_require=EXTRAS_REQUIRE,

    # Use SPDX-style license field (avoid deprecated classifier warnings)
    license="LicenseRef-Proprietary",

    # IMPORTANT: set this to the intersection your pinned deps truly support.
    python_requires=">=3.7,<3.13",

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        # "Operating System :: OS Independent",
        # "Programming Language :: Python :: 3.8",
        # "Programming Language :: Python :: 3.9",
        # "Programming Language :: Python :: 3.10",
        # "Programming Language :: Python :: 3.11",
        # "Programming Language :: Python :: 3.12",
        # Do NOT add the deprecated 'License :: Other/Proprietary License'
    ],

    # (Optional) nice-to-have metadata
    project_urls={
        "Homepage": "https://products.aspose.com/total/python-java/",
        "Releases": "https://releases.aspose.com/total/python-java/",
        "Docs": "https://docs.aspose.com/total/python-java/",
        "Samples": "https://aspose.github.io/",
    },
)
