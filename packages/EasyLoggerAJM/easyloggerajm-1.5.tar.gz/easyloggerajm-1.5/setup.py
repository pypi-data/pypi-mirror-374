from setuptools import setup
import re
project_name = 'EasyLoggerAJM'


def get_property(prop, project):
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), open(project + '/_version.py').read())
    return result.group(1)


setup(
    name=project_name,
    version=get_property('__version__', project_name),
    packages=['EasyLoggerAJM'],
    url='https://github.com/amcsparron2793-Water/EasyLoggerAJM',
    download_url=f'https://github.com/amcsparron2793-Water/EasyLoggerAJM/archive/refs/tags/{get_property("__version__", project_name)}.tar.gz',
    keywords=['logging'],
    license='MIT License',
    author='Amcsparron',
    author_email='amcsparron@albanyny.gov',
    description='logger with already set up generalized file handlers'
)
