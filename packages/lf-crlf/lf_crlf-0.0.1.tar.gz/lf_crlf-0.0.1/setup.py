from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='lf-crlf',
    version='0.0.1',
    author='farfromsouls',
    author_email='farfromsouls@gmail.com',
    description='A tool to convert line endings between LF and CRLF',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/farfromsouls/LF_CRLF',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords='line endings lf crlf convert text files',
    project_urls={
        'GitHub': 'https://github.com/farfromsouls/LF_CRLF',
        'Bug Reports': 'https://github.com/farfromsouls/LF_CRLF/issues',
    },
    python_requires='>=3.6'
)