from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='readme_llm7_gen',
    version='2025.9.71453',
    author='Eugene Evstafev',
    author_email='hi@eugene.plus',
    description='A package for generating README.md files using LLMs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/readme_llm7_gen',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
