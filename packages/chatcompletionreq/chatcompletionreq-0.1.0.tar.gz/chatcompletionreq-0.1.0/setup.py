from setuptools import setup, find_packages

setup(
    name="chatcompletionreq",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],  # list dependencies if any
    python_requires=">=3.10",  # or your Python version
    author="William Ambrosetti",
    description="A simple library to wrap chat completion requests",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/WiiLife/chatcompletionreq"
)
