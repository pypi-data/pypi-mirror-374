from setuptools import setup

__author__ = "JoOx01"
__pkg_name__ = "TempMailGenerator"
__version__ = "1.0.7"
__desc__ = """A lightweight temporary email generator built with Flask (Python) and a modern frontend. It allows you to quickly generate disposable email addresses, view incoming messages, and refresh your inbox automatically."""

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=__pkg_name__,
    version=__version__,
    packages=[__pkg_name__],
    license='MIT',
    description=__desc__,
    author=__author__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jo0x01/TempMail-Generator',
    keywords=["tempmail", "tmail", "email", "mail", "temporary-email", "disposable-mail"],
    install_requires=['flask', 'requests'],
    entry_points={
        'console_scripts': [
            'temp-mail = TempMailGenerator.main:main',
            'tmail = TempMailGenerator.main:main',
            'create-mail = TempMailGenerator.main:main',
            'generate-mail = TempMailGenerator.main:main',
            'gt-mail = TempMailGenerator.main:main',
            'gtmail = TempMailGenerator.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.1',
)
