from setuptools import setup, find_packages

setup(
    name='hnt_nf_jira_servicos_library',
    version='0.0.27',
    license='MIT License',
    author='Guillerme Rezende Manhaes',
    maintainer='Pepe',
    keywords='nota_fiscal',
    description=u'Lib to access nf from Jira',
    packages=find_packages(),
    package_data={'nf_jira': ['entities/*','entities/classes/*']},
    include_package_data=True,
    install_requires=[
        'requests',
        'pydantic>=2.5.2'
    ],
)