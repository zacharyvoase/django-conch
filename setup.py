from setuptools import setup, find_packages

setup(
    name='django-conch',
    version='0.0.1',
    description='Expose the Django shell as an SSH server.',
    author='Zachary Voase',
    author_email='z@zacharyvoase.com',
    url='https://github.com/zacharyvoase/django-conch',
    packages=find_packages(),
    install_requires=[
        'Twisted>=12.3.0',
    ],
)
