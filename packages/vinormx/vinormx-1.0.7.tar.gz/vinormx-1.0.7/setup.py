"""
Setup script cho vinormx
"""

from setuptools import setup, find_packages
import os

# Đọc README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Vietnamese Text Normalization for Windows 64-bit"

setup(
    name='vinormx',
    version='1.0.7',
    author='Nguyen Huu Thanh',
    author_email='nguyenhuuthanh@gmail.com',
    description='Advanced Vietnamese Text Normalization System - Modular Architecture with Comprehensive Dictionaries and Regex Rules',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/genievn/vinormx',
    packages=['vinormx'],
    package_data={
        'vinormx': [
            'dictionaries/*.txt',
            'RegexRule/*.txt', 
            'Dict/*.txt'
        ]
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Vietnamese',
    ],
    keywords='vietnamese text normalization nlp tts speech synthesis modular comprehensive dictionaries regex rules',
    python_requires='>=3.6',
    install_requires=[
        # Không có dependencies ngoài, chỉ sử dụng thư viện chuẩn
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'flake8',
        ],
    },
    entry_points={
        'console_scripts': [
            'vinorm-cli=vinormx:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/genievn/vinormx/issues',
        'Source': 'https://github.com/genievn/vinormx',
        'Original Vinorm': 'https://github.com/v-nhandt21/Vinorm',
        'Original C++ Version': 'https://github.com/NoahDrisort/vinorm_cpp_version',
    },
)