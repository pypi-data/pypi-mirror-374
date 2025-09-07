from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ffcapcha",
    version="1.0.0",
    author="Vnd FF",
    author_email="vandayzi12@gmail.com",
    description="service is aimed at protecting telegram bots from suspicious requests and DDoS attacks. Documentation about the module and resource news -> https://t.me/ffcapcha",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ffcapcha",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["Pillow>=8.0.0"],
    keywords="telegram, captcha, anti-spam, security",
)