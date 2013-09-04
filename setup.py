from setuptools import setup

setup(
    name='instapaperout',
    version='1.0',
    description='Save bookmarks from Instapaper to local disk',
    py_modules=['instapaperout'],
    scripts=['bin/instapaperout'],
    author='Mark Paschal',
    author_email='markpasc@markpasc.org',
    url='https://github.com/markpasc/instapaperout',
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    requires=['argh', 'arghlog', 'requests'],
    install_requires=['argh', 'arghlog', 'requests'],
)
