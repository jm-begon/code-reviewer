from setuptools import setup


setup(
    name='reviewer',
    version='1.0',
    description='Package providing the `review` command in order to review codes and share comments',
    author='Charles Ferir <charles.ferir@student.uliege.be>, Gaspard Lambrechts <gaspard.lambrechts@student.uliege.be>',
    packages=['reviewer', 'reviewer.server', 'reviewer.languages'],
    install_requires=['jinja2'],
    scripts=['scripts/review'],
    package_data={'reviewer.server': ['html/*']},
    include_package_data=True,
)