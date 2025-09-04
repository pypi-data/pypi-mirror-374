#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools,distutils,shutil,re,os

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

class up2pypi(distutils.cmd.Command):
    description='twine upload current version & update version automatic'
    user_options=[
    ]
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        f=open("setup.py","rb")
        data=f.readlines()
        f.close()
        shutil.copy2("setup.py","setup.py.bak")
        f=open("setup.py2","wb")
        for i in data:
            if re.search(b'''version\s*=\s*['"](.*)['"]''',i):
                jg=re.search(b'\d+\.\d+\.\d+',i)
                if jg:
                    oldver=jg.group()
                    s=oldver.decode("utf8").split(".")
                    i=i.decode("utf8").replace("%s.%s.%s" %(s[0],s[1],s[2]),"%s.%s.%d" %(s[0],s[1],int(s[2])+1))
                    os.system("./setup.py sdist")
                    os.system("twine upload dist/libsw3-%s.%s.%s.tar.gz" %(s[0],s[1],s[2]))
                    i=bytes(i,encoding="utf8")
            f.write(i)
        f.close()
        shutil.move("setup.py2","setup.py")

setuptools.setup(
    name="libsw3",
    version="0.3.5",
    author="Chen chuan",
    author_email="kcchen@139.com",
    description="libsw3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://svn2.rtfund.com/svn/libsw3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scripts':  [
            'sw=libsw3.sw:main',
        ],
    },
    cmdclass={
        'sc':up2pypi
    },
)
