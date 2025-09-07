from setuptools import setup, find_packages

setup(
    name='signal_ICT_AhujaSlock_92400133041',
    version='1.0.0',
    author='Ahuja Slock',
    author_email='ahuja.slock@example.com',  # Replace with actual email
    description='A Python package for signal generation and operations',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/signal_ICT_AhujaSlock_92400133041',  # Replace with actual GitHub URL
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
