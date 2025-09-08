from setuptools import setup, find_packages

setup(
    name="text2mem-cli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Command line interface for text2mem",
    long_description="This is a placeholder package for text2mem-cli",
    long_description_content_type="text/plain",
    url="https://github.com/yourusername/text2mem-cli",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
