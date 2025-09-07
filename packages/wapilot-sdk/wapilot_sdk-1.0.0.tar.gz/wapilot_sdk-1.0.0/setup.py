from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wapilot-sdk",
    version="1.0.0",
    author="WAPILOT",
    author_email="support@wapilot.io",
    description="Official Python SDK for WAPILOT.io - WhatsApp Business API Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://wapilot.io",
    project_urls={
        "Documentation": "https://docs.wapilot.io",
        "Source": "https://github.com/wapilot/wapilot-python-sdk",
        "Bug Tracker": "https://github.com/wapilot/wapilot-python-sdk/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)
