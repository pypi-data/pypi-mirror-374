from setuptools import setup, find_packages

setup(
    name='orionac-genai',
    version='0.1.0',
    packages=find_packages(),
    url='',
    license='',
    author='Zakariya',
    author_email='contact@orionac-ai.in',
    description='A wrapper for the Orionac-AI API.',
    install_requires=[
        'requests>=2.25.0',
    ],
)