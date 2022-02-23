from setuptools import setup
import re

version = ''
with open('discord/ext/help/__init__.py') as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(name='discord-ext-help',
      author='Mayerch1',
      url='https://github.com/Mayerch1/discord-ext-help',
      description='An extension module to make an interaction based help menu with PyCord',
      long_description=long_description,
      keywords='py-cord extension help interactions',
      version=version,
      packages=['discord.ext.help'],
      project_urls={
          "Bug Tracker": "https://github.com/Mayerch1/discord-ext-help/issues"
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: Other/Proprietary License',
          'Topic :: Utilities'
      ],
      python_requires='>=3.8.0',
      install_requires=['py-cord>=2.0.0b4']
      )
