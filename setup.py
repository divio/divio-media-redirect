from setuptools import find_packages, setup

from divio_media_redirect import __version__


setup(
    name="divio-media-redirect",
    version=__version__,
    description=open("README.rst").read(),
    author="Divio",
    author_email="info@divio.com",
    packages=find_packages(),
    platforms=["OS Independent"],
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)
