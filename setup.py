from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call
from distutils.command.build_py import build_py as _build_py
import sys, os.path
import re

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion
import subprocess
import platform

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + os.path.join(extdir, 'gibson2/core/render/mesh_renderer'),
                      '-DCMAKE_RUNTIME_OUTPUT_DIRECTORY=' + os.path.join(extdir, 'gibson2/core/render/mesh_renderer', 'build'),
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

'''
class PostInstallCommand(install):
        """Post-installation for installation mode."""
        def run(self):
                print('post installation')
                check_call("bash realenv/envs/build.sh".split())
                install.run(self)
'''

setup(name='gibson2',
    version='0.0.1',
    author='Stanford University',
    zip_safe=False,
    install_requires=[
            'numpy>=1.10.4',
            'pyglet>=1.2.0',
            'gym==0.9.4',
            'Pillow>=3.3.0',
            'PyYAML>=3.12',
            'numpy>=1.13',
            'pybullet==2.4.1',
            'transforms3d>=0.3.1',
            'tqdm >= 4',
            'pyzmq>=16.0.2',
            'Pillow>=4.2.1',
            'matplotlib>=2.1.0',
            'mpi4py>=2.0.0',
            'cloudpickle>=0.4.1',
            'pygame>=1.9.3',
            'opencv-python',
            'torchvision==0.2.0',
            'aenum'
    ],
    ext_modules=[CMakeExtension('CppMeshRenderer', sourcedir='gibson2/core/render')],
    cmdclass=dict(build_ext=CMakeBuild),
    tests_require=[],
)

