from setuptools import setup, find_packages

setup(
    name='k2vault',
    version='0.1.0',
    packages=find_packages(),
    authors='Alireza(a.izadshenas@k2-systems.de) Hossein(h.davoodi@k2-systems.de)',
    author_email='h.davoodi@k2-systems.de',
    description='A reusable Python module to utilize Azure KeyVaults',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/k2digidata/k2Vault',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
