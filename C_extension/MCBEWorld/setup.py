from setuptools import setup, Extension
import os

setup(
    name="MCBEWorld_C_API",
    ext_modules=[
        Extension("MCBEWorld_C_API", sources=["fast_api.c"])
    ]
)
