
from setuptools import setup
setup(
    name='pyprover9',
    version='0.0.14',
    description='Colab wrapper for the Prover9 theorem prover',
    long_description='Colab wrapper written by Brandon Bennett for the Prover9 theorem prover by William McCune.',
    #url='https://bb-ai.net/KARaML/KARaML_Tools.html',
    author='brandonb',
    author_email='B.Bennett@leeds.ac.uk',
    packages=['pyprover9'],
    #package_data= {'pyprover9':['prover9', 'diamond.p9', 'prove.p9']},
    include_package_data=True,
    classifiers=['Development Status :: 1 - Planning'],
)
