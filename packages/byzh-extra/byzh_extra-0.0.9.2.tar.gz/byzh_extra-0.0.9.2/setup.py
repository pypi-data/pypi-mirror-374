from setuptools import setup, find_namespace_packages
import byzh

setup(
    name='byzh-extra',
    version=byzh.__version__,
    author="byzh_rc",
    description="基于byzh-core的扩展包",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_namespace_packages(include=["byzh.*"]),
    install_requires=[
        'byzh_core>=0.0.9.0', # !!!!!
        'python-pptx',
        'pdf2image',
        'chardet',
        'fpdf2'
    ],
    package_data={
        'byzh_extra': ['bin/*']
    },
    entry_points={
        "console_scripts": [
            "b_py2ipynb=byzh_extra.__main__:b_py2ipynb", # b_py2ipynb 路径
            "b_ipynb2py=byzh_extra.__main__:b_ipynb2py", # b_ipynb2py 路径
            "b_str_finder=byzh_extra.__main__:b_str_finder", # b_find_str -p path -s string
        ]
    },
)
