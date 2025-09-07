from setuptools import setup, find_packages
import os

setup(
    name="photo-metadata",
    version="0.2.1",
    packages=find_packages(),
    description="Python library to extract, read, modify, and write photo and video metadata (EXIF, IPTC, XMP) using ExifTool. Supports JPEG, RAW, and video files.",
    keywords="photo, image, metadata, exif, exiftool, iptc, xmp, video, camera, photography, raw, jpeg, picture, python, library, read, write, edit",
    long_description=open(
        os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8"
    ).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kingyo1205/photo-metadata",
    author="ひろ",
    author_email="hirokingyo.sub@gmail.com",
    install_requires=[
        "tqdm",
        "chardet"
    ],
    python_requires=">=3.10",
    package_data={
        "photo_metadata": [
            "exiftool_Japanese_tag.json",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Topic :: Multimedia :: Graphics :: Capture",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://github.com/kingyo1205/photo-metadata#readme",
        "Source": "https://github.com/kingyo1205/photo-metadata",
        "Tracker": "https://github.com/kingyo1205/photo-metadata/issues",
    },
)
