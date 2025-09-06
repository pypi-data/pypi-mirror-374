from setuptools import setup, find_packages
from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    """Force building platform-specific wheel"""
    def has_ext_modules(self):
        return True

setup(
    name='CarbonX',
    version='1.0.4',
    author='Hossein Rahbar',
    author_email='rahbar.hosein@example.com',
    description='Process Design Tool for Gas-Phase Synthesis of Nanomaterials and Carbon Nanotubes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/CarbonX',  # Update if you have a repo
    packages=find_packages(),
    package_data={
        '': ['*.pyd', '*.so', '*.dll', '*.yaml', '*.yml'],
        'carbonx': ['*.pyd', '**/*.pyd'],
        'carbonx.core': ['*.pyd'],
        'carbonx.modules': ['*.pyd'],
        'carbonx.ml': ['*.pyd'],
        'carbonx.data': ['*.yaml', '*.yml', 'FFCM2.yaml'],
    },
    include_package_data=True,
    install_requires=[
        'numpy>=1.24.0,<2.0.0',  # Pin to NumPy 1.x to avoid binary incompatibility
        'scipy>=1.10.0,<1.14.0',  # Compatible with NumPy 1.x
        'matplotlib>=3.5.0',
        'pandas>=1.5.0,<2.1.0',  # Versions that work well with NumPy 1.x
        'cantera>=2.6.0',
        'Cython>=0.29.0',  # In case any runtime compilation is needed
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    python_requires='>=3.8,<3.12',  # Python version compatibility
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: Other/Proprietary License',  
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Cython',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    keywords='carbon nanotube synthesis simulation sectional-model',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/CarbonX/issues',
        'Source': 'https://github.com/yourusername/CarbonX',
        'Documentation': 'https://CarbonX.readthedocs.io',
    },
    zip_safe=False,
    distclass=BinaryDistribution,  # Critical: Forces platform-specific wheel
    entry_points={
        'console_scripts': [
            # Add any command-line scripts here if needed
            # 'carbonx-run=carbonx.cli:main',
        ],
    },
)