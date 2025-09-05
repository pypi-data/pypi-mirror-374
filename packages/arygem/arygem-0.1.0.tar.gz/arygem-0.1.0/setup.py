from setuptools import setup, find_packages

setup(
    name="arygem",  
    version="0.1.0",
    packages=find_packages(),
    install_requires=["google-genai>=0.10.0"],
    python_requires=">=3.9",
    author="Aryan Mishra",
    description="A simple Python wrapper for Google Gemini AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/arycodes/arygem",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
