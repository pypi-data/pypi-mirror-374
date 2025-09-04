from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-pagination-widget',
    version='0.1.1',
    author='Priyesh Shukla',
    author_email='priyesh.shukla070@gmail.com',
    description='A reusable Django pagination component with modern, clean styling and interactive JavaScript behavior',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/priyesh-04/django-pagination-widget',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='django pagination widget modern styling javascript',
    python_requires='>=3.9',
    install_requires=[
        'Django>=4.2',
        'tzdata; platform_system=="Windows"',
    ],
    include_package_data=True,
    zip_safe=False,
)
