from setuptools import setup, find_packages

setup(
    name="django-dtoffset-lookup",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["django"],
    author="Mayank Raichura, ChatGPT",
    author_email="mayank.raichura@gmail.com",
    description="A Django ORM custom lookup (dtoffset) for filtering DateTime fields using relative offsets.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mayankraichura/django-dtoffset-lookup",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
