from setuptools import setup, find_packages

setup(
    name='canatax',
    version='2.0.1',
    description='An easy-to-use, dependency-free Canadian sales and income tax calculator.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Michael Pearce',
    author_email='firstflush@protonmail.com',
    url='https://github.com/firstflush/canatax',
    license='MIT',
    packages=find_packages(exclude=["tests*", "*.tests"]),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    keywords='canada tax cpp ei qpp gst hst pst qst income sales payroll',
    project_urls={
        'Homepage': 'https://github.com/firstflush/canatax',
        'Bug Tracker': 'https://github.com/firstflush/canatax/issues',
        'Buy Me a Coffee': 'https://www.buymeacoffee.com/FirstFlush',
    },
)
