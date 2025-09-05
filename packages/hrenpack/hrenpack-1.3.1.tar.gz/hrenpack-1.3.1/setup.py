from setuptools import setup, find_packages

desc = '\n'.join(("Универсальная библиотека python для большинства задач", 'A universal python library for most tasks'))
req = open('requirements.txt').read().split('\n')


setup(
    name='hrenpack',
    version='1.3.1',
    author='Маг Ильяс DOMA (MagIlyas_DOMA)',
    description=desc,
    license='BSD 3-Clause License',
    long_description=open('README_PIP.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/MagIlyas-DOMA/hrenpack',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=req,
    package_data={'hrenpack': ['hrenpack/resources/*']},
    include_package_data=True,
)
