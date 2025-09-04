"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from setuptools import setup, find_packages
package_name = 'sapiens_transformers'
version = '1.2.2'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=[
        'numpy==1.25.2',
        'torch==2.4.1',
        'torchvision==0.19.1',
        'torchaudio==2.4.1',
        'accelerate==1.3.0',
        'transformers',
        'huggingface-hub',
        'requests',
        'certifi',
        'tqdm',
        'sapiens-machine',
        'sapiens-accelerator',
        'tokenizers',
        'regex',
        'datasets',
        'sentencepiece',
        'protobuf',
        'optimum',
        'einops',
        'hydra-core',
        'lightning',
        'braceexpand',
        'webdataset',
        'h5py',
        'ijson',
        'matplotlib',
        'diffusers',
        'moviepy',
        'llama-cpp-python==0.3.6',
        'llamacpp==0.1.14',
        'beautifulsoup4',
        'ftfy',
        'av',
        'tiktoken',
        'opencv-python',
        'scipy',
        'TTS==0.22.0',
        'pydub==0.25.1',
        'nemo-toolkit[all]==2.1.0',
        'megatron-core',
        'TTS',
    ],
    url='https://github.com/sapiens-technology/sapiens_transformers',
    license='Proprietary Software'
)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
