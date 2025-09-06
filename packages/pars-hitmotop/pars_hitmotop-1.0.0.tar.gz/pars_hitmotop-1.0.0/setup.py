from setuptools import setup

version='1.0.0'

with open('README.md', encoding='utf-8') as f:
    long_description=f.read()

setup(
    name = 'pars_hitmotop',
    version = version,

    author = 'Joy_079',
    author_email = 'Prufu@yandex.ru',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/JoyHubN/pars_hitmos',
    download_url = f'https://github.com/JoyHubN/pars_hitmos/arhive/v{version}.zip',
    install_requires = ['beautifulsoup4==4.13.4',
                      'fake-useragent==2.2.0',
                      'requests==2.32.4',
                      'tenacity==9.1.2',
                      ],
    # license=...,
    packages = ['parse_hitmos'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)