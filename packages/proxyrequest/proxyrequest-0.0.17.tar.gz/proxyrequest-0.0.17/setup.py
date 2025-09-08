from setuptools import setup, find_packages

setup(
    name="proxyrequest",  # Name of your package
    version="0.0.17",  # Initial version
    install_requires=[
        "fake-useragent==2.2.0",
        "tldextract==5.3.0",
        "selenium==4.35.0",
        "requests",
        "webdriver-manager==4.0.2",
        "filetype==1.2.0",
    ],
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="A Python package for making HTTP requests with proxy support and fetching HTML content using requests or Selenium.",
    long_description=open('README.md').read(),  # Optional: include a README
    long_description_content_type="text/markdown",
    packages=find_packages(),  # This will find all the packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
