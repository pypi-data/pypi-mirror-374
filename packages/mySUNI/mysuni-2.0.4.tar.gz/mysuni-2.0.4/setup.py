from setuptools import setup, find_packages
import os

# __init__.py에서 버전 정보 읽기
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'mySUNI', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '2.0.2'

# README.md 파일 읽기
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='mySUNI',
    version=get_version(),
    author='BAEM1N, Teddy Lee',
    author_email='baemin.dev@gmail.com, teddylee777@gmail.com',
    description='mySUNI CDS - 데이터 과학 교육용 라이브러리',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/braincrew/cds',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires=[
        'tqdm',
        'scikit-learn',
        'pandas',
        'matplotlib',
        'seaborn',
        'jupyter',
        'ipywidgets',
        'requests',
        'numpy',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'black',
            'flake8',
            'twine',
            'wheel',
            'build',
        ],
    },
    keywords=['mySUNI', 'CDS', 'data science', 'education', 'machine learning'],
    project_urls={
        'Bug Reports': 'https://github.com/braincrew/cds/issues',
        'Source': 'https://github.com/braincrew/cds',
        'Documentation': 'https://github.com/braincrew/cds/wiki',
    },
    include_package_data=True,
    zip_safe=False,
)
