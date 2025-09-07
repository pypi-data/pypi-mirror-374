from setuptools import setup, find_packages

setup(
    name="ffcapcha",
    version="0.1.0",
    author="Vnd FF",
    author_email="vandayzi12@gmail.com",
    description="service is aimed at protecting telegram bots from suspicious requests and DDoS attacks. Documentation about the module and resource news -> https://t.me/ffcapcha",
    long_description="service is aimed at protecting telegram bots from suspicious requests and DDoS attacks. Documentation about the module and resource news -> https://t.me/ffcapcha",
    long_description_content_type="text/plain",
    packages=find_packages(),
    install_requires=[
        "Pillow>=8.0.0",
        "python-telegram-bot>=20.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)