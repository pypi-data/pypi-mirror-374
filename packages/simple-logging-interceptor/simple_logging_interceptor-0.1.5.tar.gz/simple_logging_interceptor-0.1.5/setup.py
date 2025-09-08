from setuptools import setup, find_packages

setup(
    name="simple-logging-interceptor",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[],
    description="A simple Python decorator for logging function calls, arguments, return values, execution time, and exceptions.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mahmoud Samir",
    author_email="mahmoudsamir8998@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
