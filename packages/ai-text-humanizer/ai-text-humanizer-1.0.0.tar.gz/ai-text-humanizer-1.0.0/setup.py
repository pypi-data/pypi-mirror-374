from setuptools import setup, find_packages

setup(
    name="ai-text-humanizer",
    version="1.0.0",
    description="AI-powered text humanizer for English and Persian (فارسی)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/mohammadham/AI-Text-Humanizer",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "spacy",
        "nltk",
        "sentence-transformers",
        "hazm",
        "stanza",
        "transformers"
    ],
    entry_points={
        "console_scripts": [
            "ai-text-humanizer=ai_text_humanizer.cli:main"
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: Persian",
    ],
)
