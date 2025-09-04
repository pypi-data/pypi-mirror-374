from setuptools import setup, find_packages

setup(
    name='amusic',
    version='2.4.5',
    packages=find_packages(),
    install_requires=[
        'mido',
        'pygame'
    ],
    author='SolamateanTehCoder',
    description='A MIDI visualizer with VFX.',
    package_data={'amusic': ['*.sf2']},
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SolamateanTehCoder/amusic',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
