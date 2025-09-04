from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r', encoding='utf-8') as f:
    return f.read()

setup(
  name='magnuslib',
  version='0.0.12',
  author='sergey_k',
  author_email='qwertyz19861@gmail.com',
  description='My_library',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/magnusred1986',
  packages=find_packages(),
  install_requires=['pywin32', 'openpyxl', 'pandas', 'msoffcrypto-tool'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='my library',
  project_urls={
    'GitHub': 'https://github.com/magnusred1986'
  },
  python_requires='>=3.10'
)