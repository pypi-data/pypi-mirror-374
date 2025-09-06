from setuptools import setup

setup(
    name='iptv9',  # Lowercase, unique on PyPI
    version='0.0.3',
    py_modules=['iptv9'],  # Matches your filename
    entry_points={
        'console_scripts': [
            'iptv9 = iptv9:main',  # CLI command: maps to iptv9.py:main()
        ],
    },
    author='ssskingsss12',
    author_email='smalls3000i@gmail.com',
    description='IPTV Scanner',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.12',
)

