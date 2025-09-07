from setuptools import setup, find_packages

setup(
    name="aistv",
    version="1.4.7",
    description="STV AI Chatbot Library for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Trọng Phúc",
    author_email="phuctrongytb16@gmail.com",
    url="https://github.com/phuctrong1tuv",
    packages=find_packages(),
    python_requires=">=3.8, <3.13",
    install_requires=[
        "requests",
        "groq", 
        "pydantic"
        
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Discord": "https://discord.gg/fTaCmdxG9H",
        "TikTok": "https://vm.tiktok.com/@aistvchat",
        "GitHub": "https://github.com/phuctrong1tuv"
        
    },
    keywords="chatbot ai stv discord tiktok",
)