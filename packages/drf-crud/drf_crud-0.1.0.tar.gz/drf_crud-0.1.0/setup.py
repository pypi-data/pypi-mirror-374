from setuptools import setup, find_packages

setup(
    name="drf-crud",
    version="0.1.0",
    description="A Django REST Framework package for automatic CRUD generation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Abdulmumin Abubakar",
    author_email="abdulmumina535@gmail.com",
    url="https://github.com/codesmith-abba/drf-crud",
    packages=find_packages(),
    install_requires=[
        "djangorestframework>=3.12.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
