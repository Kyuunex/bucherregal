from distutils.core import setup

setup(
    name='bucherregal',
    packages=[
        'bucherregal',
        'bucherregal.blueprints',
        'bucherregal.classes',
        'bucherregal.reusables'
    ],
    include_package_data=True,
    package_data={'bucherregal': ['static/*', 'templates/*']},
    version="0.0.1",
    description='Book Giveaway Service',
    author='Kyuunex',
    author_email='kyuunex@protonmail.ch',
    url='https://github.com/Kyuunex/bucherregal',
    install_requires=[
        'flask',
        'pyotp',
        'feedgen',
    ],
)
