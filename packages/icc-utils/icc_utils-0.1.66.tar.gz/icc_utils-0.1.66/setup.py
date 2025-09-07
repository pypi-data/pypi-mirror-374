from setuptools import setup, find_packages

setup(
    name='icc_utils',
    version='0.1.66',
    packages=find_packages(),
    description='Package used to handle common functions at ICC',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jordan Bradley',
    author_email='jbradley@icc-ims.com',
    url='https://github.com/jbradleyicc/icc_utils',
    install_requires=[
        'sqlalchemy >= 2.0.27',
        'pyodbc >= 5.1.0',
        'pandas >= 2.2.1',
        'tqdm >= 4.66.2'
    ],
    classifiers=[
            # Choose your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    python_requires='>=3.9'
)