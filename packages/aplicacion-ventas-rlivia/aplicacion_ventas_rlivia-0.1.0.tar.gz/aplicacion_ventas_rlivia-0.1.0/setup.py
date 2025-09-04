from setuptools import setup, find_packages

setup(
    name = 'aplicacion_ventas_rlivia',
    version= '0.1.0',
    author= 'Ray Livia',
    author_email= 'rayoliviap@gmail.com',
    description= 'Paquete para gestionar ventas, impuestos y descuentos',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url = 'https://github.com/curso_python/aplicativoventas',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License", # <-- Esta línea fue corregida
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.7'
    
)