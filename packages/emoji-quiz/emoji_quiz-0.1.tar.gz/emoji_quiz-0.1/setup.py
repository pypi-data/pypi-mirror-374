from setuptools import setup, find_packages

setup(
    name="emoji-quiz",
    version="0.1",
    packages=find_packages(),
    install_requires=[],  # add Python dependencies if any
    entry_points={
        'console_scripts': [
            'emoji-quiz = emoji_quiz.main:main',  # run main() from main.py
        ],
    },
    python_requires='>=3.6',
    author="Ayaan Syed",
    author_email="syedayyan2002@gmail.com",
    description="Fun CLI game to guess movies using emojis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/Ayansyd/emoji-quiz",  # optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
