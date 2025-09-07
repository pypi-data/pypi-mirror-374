
from setuptools import setup, find_packages

setup(
    name="print_fa",
    version="0.1.0",
    author="httex",
    author_email="your.email@example.com", # Placeholder, user can change later
    description="A Python library for correct printing of Persian (Farsi) text with RTL support and styling options.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/httex/print_fa", # Placeholder, user can change later
    packages=find_packages(),
    install_requires=[
        "arabic-reshaper",
        "python-bidi",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Natural Language :: Persian",
    ],
    python_requires=">=3.6",
)


