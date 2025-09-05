from setuptools import find_packages, setup

with open("./README.md", "r") as f:
    long_description = f.read()

setup(
    name="django_hls",
    version="1.5.9",
    description="django-hls is a reusable Django application for streaming video and audio using the HLS",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YasinKar/django_hls",
    author="Yasin Karbasi",
    author_email="yasinkardev@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "bson >= 0.5.10",
        
        "Django>=5.2.2,<6.0",                  
        "celery>=5.5.3,<6.0",                  
        "ffmpeg-progress-yield>=0.12.0,<1.0", 
        "ffmpeg-python>=0.2.0,<0.3" 
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.10",
    keywords="stream django hls",
)