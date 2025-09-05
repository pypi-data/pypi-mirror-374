from distutils.core import setup

VERSION = "1.6.1"
setup(
    name="pyEager",
    packages=["pyEager"],
    version=VERSION,
    license="MIT",
    description="A simple package to read in eager results.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Thiseas C. Lamnidis",
    author_email="thisseass@gmail.com",
    url="https://github.com/TCLamnidis/pyEager",
    download_url=f"https://github.com/TCLamnidis/pyEager/archive/refs/tags/{VERSION}.tar.gz",
    keywords=["python", "pandas", "nf-core", "eager", "nf-core/eager", "ancient DNA"],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
        "numpy",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        # 'Intended Audience :: Developers',      # Define that your audience are developers
        # 'Topic :: Software Development :: Build Tools',
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
