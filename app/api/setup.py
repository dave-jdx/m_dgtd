from distutils.core import setup
from Cython.Build import cythonize

# setup(ext_modules=cythonize("api_mesh.py"))
# setup(ext_modules=cythonize("api_model.py"))
# setup(ext_modules=cythonize("api_vtk.py"))
setup(ext_modules=cythonize("api_reader.py"))
# setup(ext_modules=cythonize("api_project.py"))
# setup(ext_modules=cythonize("api_license.py"))
# setup(ext_modules=cythonize("api_config.py"))

#python setup.py build_ext --inplace


