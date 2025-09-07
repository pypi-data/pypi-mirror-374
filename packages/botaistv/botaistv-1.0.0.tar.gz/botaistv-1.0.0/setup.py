from setuptools import setup, find_packages

setup(
    name="botaistv",
    version="1.0.0",
    description="STV AI Chatbot Library for Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Trọng Phúc",
    author_email="phuctrongytb16@gmail.com",
    url="https://github.com/phuctrong1tuv",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "stv=botaistv.cli:main",
        ],
    },
    project_urls={
        "TikTok": "https://vm.tiktok.com/@aistvchat",
        "GitHub": "https://github.com/phuctrong1tuv"
    },
    keywords="chatbot ai stv termux",
)