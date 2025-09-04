from setuptools import setup

setup(
  name='structured_log',
  version='1.10',
  description='Structured logging',
  author='Alex Yung',
  packages=['structured_logging'],
  zip_safe=False,
  install_requires=[
    'structlog',
  ],
  package_data={'': ['structured_logging.pyd']},
  include_package_data = True,
)
