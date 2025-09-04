from setuptools import setup, find_packages

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="desklog",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A desktop logging application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/desklog",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=["flask", "requests"],
    entry_points={
        "console_scripts": ["desklog=desklog.server:start"]
    },
)
