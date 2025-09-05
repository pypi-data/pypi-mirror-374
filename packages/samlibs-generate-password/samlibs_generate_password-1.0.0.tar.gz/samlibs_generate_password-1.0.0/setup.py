from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="samlibs-generate-password",
    version="1.0.0",
    author="themrsami",
    author_email="usamanazir13@gmail.com",
    description="A lightweight, fast, and optimized password generator library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/themrsami/samlibs-generate-password-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ],
    python_requires=">=3.6",
    install_requires=[],  # No dependencies - ultra lightweight!
    keywords=[
        "password",
        "generator",
        "random",
        "security",
        "lightweight",
        "fast",
        "samlibs",
        "cryptography"
    ],
    project_urls={
        "Bug Reports": "https://github.com/themrsami/samlibs-generate-password-python/issues",
        "Source": "https://github.com/themrsami/samlibs-generate-password-python",
        "Documentation": "https://github.com/themrsami/samlibs-generate-password-python#readme"
    }
)