"""
AI Image Platform Setup Configuration
=====================================

Python package setup for the AI Image Platform library.
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def read_version():
    with open('ai_image_platform/__init__.py', 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

# Read long description from README
def read_long_description():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return """
    AI Image Platform - Comprehensive Python library for AI-powered image processing,
    generation, editing, and multimodal chat capabilities.
    """

# Read requirements
def read_requirements():
    requirements = [
        'flask>=2.3.0',
        'google-genai>=1.33.0',
        'pillow>=10.0.0',
        'requests>=2.31.0',
        'werkzeug>=2.3.0',
        'gunicorn>=21.2.0'
    ]
    
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            file_requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            # Merge with default requirements, preferring file versions
            for req in file_requirements:
                package_name = req.split('>=')[0].split('==')[0].split('<=')[0]
                # Remove any existing requirement with same package name
                requirements = [r for r in requirements if not r.startswith(package_name)]
                requirements.append(req)
    
    return requirements

setup(
    name='ai-image-platform',
    version=read_version(),
    author='AI Image Platform Team',
    author_email='contact@ai-image-platform.dev',
    description='Comprehensive Python library for AI-powered image processing and multimodal chat',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-username/ai-image-platform',
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=6.0.0',
            'sphinx-rtd-theme>=1.2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'ai-image-platform=ai_image_platform.api.flask_app:main',
        ],
    },
    include_package_data=True,
    package_data={
        'ai_image_platform': [
            'templates/*.html',
            'static/css/*.css',
            'static/js/*.js',
        ],
    },
    keywords=[
        'ai', 'artificial intelligence', 'image processing', 'image generation',
        'image analysis', 'computer vision', 'gemini ai', 'multimodal chat',
        'flask api', 'serverless', 'pollinations', 'text-to-image'
    ],
    project_urls={
        'Documentation': 'https://your-domain.com/docs',
        'Source': 'https://github.com/your-username/ai-image-platform',
        'Bug Reports': 'https://github.com/your-username/ai-image-platform/issues',
    },
)