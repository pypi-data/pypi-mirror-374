import setuptools
from pathlib import Path

# Importamos el texto que hemos escrito en README.md y
# la guardamos en un variable para luego utilizarla.
long_desc = Path("README.md").read_text()

setuptools.setup(
    # El nombre del paquete que va tener dentro de pypi.
    name="holamundoplayer-pizarro05",
    # Indicamos la version que queremos utilizar
    version="0.0.1",
    # Aqui le vamos a dar una descripcion larga en pypi
    long_description=long_desc,
    # Donde se encuentran los paquetes
    packages=setuptools.find_packages(
        exclude=["mocks", "test"]
    )
)
