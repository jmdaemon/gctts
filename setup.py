from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gctts",
    version="0.1.0",
    license='MIT',
    author="Joseph Diza",
    author_email="josephm.diza@gmail.com",
    description="TTS cli tool to query Google Cloud's Text-To-Speech API to generate audio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jmdaemon/gctts",
    project_urls={ "Bug Tracker": "https://github.com/jmdaemon/gctts/-/issues", },
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where='.'),
    python_requires=">=3.6",
    install_requires=['loguru', 'toml', 'requests'],
    scripts=[],
    entry_points={
        'console_scripts': [
            'tts = tts:main',
        ],
    },
    test_suite='tests',
)
