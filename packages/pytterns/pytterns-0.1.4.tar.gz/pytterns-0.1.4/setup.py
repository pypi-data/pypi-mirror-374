from setuptools import setup

setup(
    name="pytterns",
    # version is managed by setuptools_scm (from git tags)
    use_scm_version=True,
    author="Marcos Rosa",
    author_email="marcos.cantor@gmail.com",
    description="A library to easily use design patterns with Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=["pytterns", "pytterns.core"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "dev": ["pytest"],
    },
)
