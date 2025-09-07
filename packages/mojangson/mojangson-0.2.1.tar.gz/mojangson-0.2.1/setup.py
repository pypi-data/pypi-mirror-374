from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='mojangson',
    version='0.2.1',
    author='mushroomforyou',
    author_email='mushroomforus@gmail.com',
    description='Python Mojangson parser',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/MushroomForYou/mojangson',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mojangson=mojangson.cli:main"
        ],
    },
    install_requires=['lark>=1.2.2'],
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='json mojang nbt parser',
    project_urls={
        'GitHub': 'https://github.com/MushroomForYou/mojangson'
    },
    python_requires='>=3.10'
)
