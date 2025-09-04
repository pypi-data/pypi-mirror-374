from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agnost",
    version="0.1.0",
    author="Agnost AI",
    author_email="founders@agnost.ai",
    description="Analytics SDK for Model Context Protocol Servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agnost-ai/analytics-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/agnost-ai/analytics-sdk/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)
