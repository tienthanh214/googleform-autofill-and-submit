import sys
import setuptools

# Ensure the correct version of Python is being used
if not sys.version_info >= (3, 6):
    sys.exit("Sorry, Python >= 3.6 is required")

# Read the requirements from the requirements.txt file
with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="googleform-toolkit",
    version="0.0.1",
    author="Tien-Thanh Nguyen-Dang",
    author_email="ndtthanh214@gmail.com",
    description="Toolkit to automate filling and submitting Google Form",
    long_description="Toolkit to automate filling and submitting Google Form",
    long_description_content_type="text",
    license='LICENSE.txt',
    packages=setuptools.find_packages(),
    install_requires=required,
    classifiers=['Operating System :: POSIX', ],
    python_requires='>=3.6',
)