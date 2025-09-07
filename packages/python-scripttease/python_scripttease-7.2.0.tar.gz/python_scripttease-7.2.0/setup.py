# See https://packaging.python.org/en/latest/distributing.html
# and https://docs.python.org/2/distutils/setupscript.html
# and https://pypi.python.org/pypi?%3Aaction=list_classifiers
from setuptools import setup, find_packages


def read_file(path):
    with open(path, "r") as f:
        contents = f.read()
        f.close()
    return contents


setup(
    name='python-scripttease',
    version=read_file("VERSION.txt"),
    description=read_file("DESCRIPTION.txt"),
    long_description=read_file("README.markdown"),
    long_description_content_type="text/markdown",
    author='Shawn Davis',
    author_email='shawn@develmaycare.com',
    url='https://develmaycare.com/products/python/scripttease/',
    download_url='https://gittraction.com/diff6/python-scripttease',
    project_urls={
        'Documentation': "https://docs.diff6.com/en/python-scripttease/latest/",
        'Source': "https://gittraction.com/diff6/python-scripttease",
        'Tracker': "https://gittraction.com/diff6/python-scripttease/issues"
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "colorama",
        "jinja2",
        "Markdown",
        "pygments",
        "python-commonkit",
        "pyyaml",
        "tabulate",
    ],
    # dependency_links=[
    #     "https://github.com/develmaycare/superpython",
    # ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=False,
    # tests_require=[
    #     "coverage",
    #     "pytest",
    # ],
    # test_suite='runtests.runtests',
    entry_points={
      'console_scripts': [
          'tease = scripttease.cli:main_command',
      ],
    },
)
