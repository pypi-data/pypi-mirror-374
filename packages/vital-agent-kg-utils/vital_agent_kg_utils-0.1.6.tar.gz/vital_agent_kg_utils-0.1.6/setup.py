from setuptools import setup, find_packages

setup(
    name='vital-agent-kg-utils',
    version='0.1.6',
    author='Marc Hadfield',
    author_email='marc@vital.ai',
    description='Vital Agent KG Utils',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vital-ai/vital-agent-kg-utils',
    packages=find_packages(),
    license='Apache License 2.0',
    install_requires=[
            'vital-ai-vitalsigns>=0.1.32',
            'vital-agent-container-sdk>=0.1.5',
            'vital-ai-haley-kg>=0.1.24',
            'kgraphservice>=0.0.8',
            'six',
            'pyyaml',
            'requests',
            'pydantic>=2.9.1'
        ],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
