from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="OTAKUGIFS",
    version="1.0.3",
    author="INFINITE_.",
    author_email="work4infinite@gmail.com",
    description="A Python wrapper for the OtakuGIFS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/infinite31/OTAKUGIFS",
    packages=find_packages(),
    install_requires=[
        'httpx'
    ],
    classifiers=classifiers,
    python_requires='>=3.6',
    keywords=['python', 'gif-generator', 'anime', 'api', 'wrapper'],
)