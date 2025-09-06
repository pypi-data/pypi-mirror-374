#!/usr/bin/env python3
"""
Setup configuration for AdsonAI Python SDK v2.0
Enhanced SDK with separate ad/conversation consumption
"""

from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
def get_version():
    with open(os.path.join('adsonai_sdk', '__init__.py'), 'r') as f:
        content = f.read()
        match = re.search(r'__version__ = [\'"]([^\'"]+)[\'"]', content)
        if match:
            return match.group(1)
    raise RuntimeError('Unable to find version string.')

# Read README for long description
def get_long_description():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "AdsonAI Python SDK - AI-powered contextual advertising platform"

# Read requirements
def get_requirements():
    try:
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return [
            'requests>=2.25.0',
            'urllib3>=1.26.0'
        ]

setup(
    name='adsonai-sdk',
    version=get_version(),
    author='AdsonAI Team',
    author_email='developers@adsonai.com',
    description='Python SDK for AdsonAI contextual advertising platform',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/adsonai/adsonai-python-sdk',
    project_urls={
        'Homepage': 'https://adsonai.com',
        'Documentation': 'https://docs.adsonai.com',
        'Repository': 'https://github.com/adsonai/adsonai-python-sdk',
        'Bug Tracker': 'https://github.com/adsonai/adsonai-python-sdk/issues',
        'API Dashboard': 'https://adsonai.vercel.app/api-keys',
        'Support': 'mailto:developers@adsonai.com'
    },
    packages=find_packages(exclude=['tests*', 'examples*', 'docs*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Natural Language :: English',
    ],
    keywords=[
        'adsonai', 'advertising', 'ai', 'contextual', 'ads', 'monetization', 
        'chatbot', 'ecommerce', 'content', 'marketing', 'sdk', 'api'
    ],
    python_requires='>=3.7',
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-asyncio>=0.14.0',
            'pytest-mock>=3.0.0',
            'pytest-cov>=2.10.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'mypy>=0.800',
            'pre-commit>=2.0.0',
            'twine>=3.0.0',
            'wheel>=0.36.0'
        ],
        'performance': [
            'aiohttp>=3.7.0',  # For future async support
            'ujson>=4.0.0',    # Faster JSON parsing
            'orjson>=3.0.0'    # Even faster JSON (optional)
        ],
        'analytics': [
            'pandas>=1.2.0',
            'matplotlib>=3.3.0',
            'numpy>=1.19.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'adsonai=adsonai_sdk.cli:main',  # Future CLI tool
        ],
    },
    package_data={
        'adsonai_sdk': [
            'py.typed',  # Indicates package supports type hints
        ],
    },
    include_package_data=True,
    zip_safe=False,  # Required for proper import handling
    
    # Additional metadata for PyPI
    platforms=['any'],
    license='MIT',
    
    # Test configuration
    test_suite='tests',
    tests_require=[
        'pytest>=6.0.0',
        'pytest-mock>=3.0.0',
        'responses>=0.20.0'
    ],
    
    # Documentation configuration
    command_options={
        'build_sphinx': {
            'project': ('setup.py', 'AdsonAI SDK'),
            'version': ('setup.py', get_version()),
            'release': ('setup.py', get_version()),
        }
    },
)

# Post-install message
print(f"""
🚀 AdsonAI SDK v{get_version()} installed successfully!

Next_steps:
1. Get your API key: https://adsonai.vercel.app/api-keys
2. Quick start: python -c "from adsonai_sdk import quick_start_guide; quick_start_guide()"
3. Documentation: https://docs.adsonai.com/sdk/python

New in v2.0:
✅ Separate ads and conversation consumption
✅ Enhanced AI matching with intent detection  
✅ Advanced context and personalization
✅ Built-in caching and performance optimization
✅ Full backward compatibility

Happy advertising! 🎯
""")