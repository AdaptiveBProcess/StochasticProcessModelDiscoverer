from setuptools import setup, find_packages

setup(name='sp_model_discoverer',
      version='1.0.0',
      description='stochastic process model discoverer',
      author='Manuel Camargo',
      url='https://github.com/AdaptiveBProcess/StochasticProcessModelDiscoverer',
      package_dir={"": "src"},
      packages=find_packages(where='src'),
      install_requires=[
          'pandas==1.5.3',
          'networkx==3.0',
          'numpy==1.24.2',
          'scikit-learn==1.2.2',
          'hyperopt==0.2.5',
          'jellyfish==0.9.0',
          'opyenxes==0.3.0',
          'pm4py==2.6.1',
          'gensim==4.3.1',
          'fitter==1.5.2',
          'pyyaml==6.0',
          'click~=8.1.3',
          'lxml~=4.9.2',
          'tqdm~=4.65.0'],
      entry_points={
        'console_scripts': [
            'spmd = pipeline:main',
        ]
    }
)
