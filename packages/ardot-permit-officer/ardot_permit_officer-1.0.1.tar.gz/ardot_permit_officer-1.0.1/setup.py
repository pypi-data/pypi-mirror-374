from setuptools import setup, find_packages

setup(
    name="ardot_permit_officer",
    version="0.1.0",
    description="Fetch ARDOT permit officer contact info from all 10 district pages.",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/yourusername/ardot_permit_officer",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4"
    ],
    entry_points={
        "console_scripts": [
            "ardot-permit-officer=ardot_permit_officer.cli:main"
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
