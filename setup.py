from setuptools import setup
import os

# from https://stackoverflow.com/questions/27664504/how-to-add-package-data-recursively-in-python-setup-py
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('reviewer/html')



setup(
    name='reviewer',
    version='1.0',
    description='Package providing the `review` command in order to review codes and share comments',
    author='Charles Ferir <charles.ferir@student.uliege.be>, Gaspard Lambrechts <gaspard.lambrechts@student.uliege.be>',
    packages=['reviewer'],
    install_requires=['jinja2', 'Pygments'],
    scripts=['review'],
    package_data={'reviewer': extra_files},
    include_package_data=True,
)