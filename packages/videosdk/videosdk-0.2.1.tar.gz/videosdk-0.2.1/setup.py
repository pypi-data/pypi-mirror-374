import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="videosdk",
    version="0.2.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="videosdk",
    author_email="sdk@videosdk.live",
    license="MIT",
    packages=setuptools.find_packages(include=["videosdk*"], exclude=["example"]),
    include_package_data=True,
)
