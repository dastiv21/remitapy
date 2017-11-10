from setuptools import setup
from remitapy import version

setup(name='remitapy',
      version=version.__version__,
      description='Remita Payment Gateway v1.6 python package',
      url='http://github.com/storborg/funniest',
      author=version.__author__,
      author_email=version.__email__,
      license=version.__license__,
      packages=['remitapy'],
      install_requires =[
          'pycrypto==2.6',
          'requests'
      ],
      zip_safe=False)
