version = '202509050851'

requirements = [
    'jupyter',
    'ipywidgets',
    'checkmarkandcross',
    'jupyter-duckdb>=1.2.101',
    'beautifulsoup4~=4.12',
    'kaleido~=1.0',
    'matplotlib~=3.10',
    'networkx~=3.5',
    'nltk~=3.9',
    'numpy~=1.26',  # gensim, spaCy require <2.0
    'pandas~=2.2',
    'pillow~=11.1',
    'plotly~=6.1',
    'pyyaml~=6.0',
    'requests~=2.32',
    'scikit-learn~=1.6',
    'scipy~=1.13',  # gensim requires <1.14
    'torch~=2.6',  # See also Dockerfile for torch dependency!
    'transformers~=4.50',
    'gensim~=4.3.3',
    'geopandas~=1.1.0',
    'pygwalker~=0.4.9',
    'spacy~=3.8.4',
    'statsmodels~=0.14.4',
    'fa2_modified==0.3.10',
    'grizzly_sql==0.1.5.post1',  # newer grizzly versions require additional dependencies!
    'HanTa==1.1.2',
    'Levenshtein==0.27.1',
    'pke@git+https://github.com/boudinfl/pke.git#egg=pke',
]

if __name__ == '__main__':
    from setuptools import setup, find_packages
    setup(
        name='tui_dsg',
        version=version,
        author='Eric Tröbs',
        author_email='eric.troebs@tu-ilmenau.de',
        description='everything you need for our jupyter notebooks',
        long_description='everything you need for our jupyter notebooks',
        long_description_content_type='text/markdown',
        url='https://dbgit.prakinf.tu-ilmenau.de/lectures/data-science-grundlagen',
        project_urls={},
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        python_requires='>=3.10',
        install_requires=[
            r
            for r in requirements
            if '@' not in r
        ],
        package_data={
            'tui_dsg': [
                'datasets/resources/*',
                'datasets/swapi/*',
            ]
        },
        include_package_data=True
    )
