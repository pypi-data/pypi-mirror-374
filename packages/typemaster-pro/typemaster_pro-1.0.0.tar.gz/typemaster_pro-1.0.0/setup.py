from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="typemaster-pro",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced Terminal Typing Suite with User Management and Statistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/typemaster-pro",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "typemaster=typemaster_pro:main",
        ],
    },
    include_package_data=True,
)
