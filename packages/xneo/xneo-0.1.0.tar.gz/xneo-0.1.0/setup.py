from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xneo",
    version="0.1.0",
    author="NeoAI",
    author_email="info@khulnasoft.com",
    description="XNeo - A lightweight CLI tool for executing and serving AI flows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neopilot-ai/xneo",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="utilities tools development",
    project_urls={
        "Bug Reports": "https://github.com/neopilot-ai/xneo/issues",
        "Source": "https://github.com/neopilot-ai/xneo",
    },
)
