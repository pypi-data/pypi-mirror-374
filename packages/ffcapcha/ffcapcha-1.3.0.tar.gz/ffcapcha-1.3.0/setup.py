from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

setup(
    name="ffcapcha",
    version="1.3.0",
    author="VndFF, pavyk",
    author_email="vandayzi12@gmail.com",
    description="service is aimed at protecting telegram bots from suspicious requests and DDoS attacks. Documentation about the module and resource news -> https://t.me/ffcapcha",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skoro_budet/ffcapcha",
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
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)