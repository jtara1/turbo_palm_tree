from distutils.core import setup
import sys
import re


def get_install_requirements():
    requirements = []
    with open('requirements.txt', 'r') as f:
        for line in f:
            requirements.append(re.sub("\s", "", line))
    print(requirements)
    return requirements

if __name__ == "__main__":
    get_install_requirements()
    sys.exit(0)

setup(name='tpt',
      version='v0.2',
      description='Download image from subreddits',
      author='James T',
      author_email='jtara@tuta.io',
      url='https://github.com/jtara1/turbo_palm_tree',
      install_requires=get_install_requirements(),
      )
