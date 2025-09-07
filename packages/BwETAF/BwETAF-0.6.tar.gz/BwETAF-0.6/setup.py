from setuptools import setup, find_packages

setup(
    name="BwETAF",
    version="0.6",
    packages=find_packages(include=["BwETAF", "BwETAF.*"]),
    include_package_data=True,
    install_requires=[
        "flax",
        "jax",
        "huggingface_hub",
        "optax",
        "numpy",
        "tiktoken",
        "flash_attention_jax",
        "tokenizers"
    ],
    description="Module to load BwETAF models (Flax)",
    author="Boring._.wicked",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)