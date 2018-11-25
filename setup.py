import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easy_rate",
    version="0.0.1",
    author="Stephen Zhuang",
    author_email="stephen.zhuang@gmail.com",
    description="Just another homework project for fun",
    include_package_data=True,
    install_requires=[
        'aiohttp==3.4.4',
        'Click==7.0',
        'pandas==0.23.4',
        'tablib==0.12.1',
        'tenacity==5.0.2',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/everbird/easy_rate",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'easy-rate=easy_rate.cli:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
