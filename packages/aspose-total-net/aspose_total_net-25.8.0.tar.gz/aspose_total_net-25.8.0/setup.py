from setuptools import setup

NAME = "aspose-total-net"
VERSION = "25.8.0"

REQUIRES = [
    "aspose-3d==25.8.0",
    "aspose-barcode-for-python-via-net==25.7",
    "aspose-cells-python==25.8.0",
    "aspose-diagram-python==25.8",
    "Aspose.Email-for-Python-via-NET==25.8",
    "aspose-finance==25.3",
    "aspose-gis-net==25.8.0",
    "aspose-html-net==25.8.0",
    "aspose-imaging-python-net==25.7.0",
    "aspose-ocr-python-net==25.8.0",
    "aspose-page==25.8.0",
    "aspose-pdf==25.8.0",
    "aspose-psd==25.8.0",
    "aspose-slides==25.8.1",
    "aspose-svg-net==25.8.0",
    "aspose-tasks==25.8.0",
    "aspose-tex-net==25.8.0",
    "aspose-words==25.8.0",
    "aspose-zip==25.8.0",
]

setup(
    name=NAME,
    version=VERSION,
    description=(
        "Aspose.Total for Python via .NET is a Document Processing python class "
        "library that allows developers to work with Microsoft Word®, Microsoft PowerPoint®, "
        "Microsoft Outlook®, OpenOffice®, & 3D file formats without needing Office Automation."
    ),
    url="https://releases.aspose.com/total/python-net/",
    author="Aspose",
    author_email="total@aspose.com",
    packages=["aspose-total-net"],
    include_package_data=True,
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=REQUIRES,
    zip_safe=False,

    # SPDX-style license field instead of deprecated classifier
    license="LicenseRef-Proprietary",

    python_requires=">=3.6,<3.12",

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    # 'platforms' is optional; classifiers above are what tools read
)
