from setuptools import setup, find_packages

setup(name='posio',
      description='A multiplayer geography game using Websockets',
      version='0.1',
      author='Arthur Brenaut',
      author_email='arthur.brenaut@gmail.com',
      packages=find_packages(),
      install_requires=[
          'flask',
          'flask-socketio',
          'eventlet'
      ],
      zip_safe=False)
