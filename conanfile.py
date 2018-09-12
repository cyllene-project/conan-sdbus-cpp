import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class SdbuscppConan(ConanFile):
    name = "sdbus-cpp"
    version = "0.3.1"
    license = "https://github.com/Kistler-Group/sdbus-cpp/blob/master/COPYING"
    url = "https://github.com/chebizarro/conan-sdbus-ccp"
    description = "D-Bus IPC C++ binding library built on top of sd-bus, a D-Bus C library by systemd"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "cppstd": [11, 17]}
    default_options = "shared=False", "fPIC=True", "cppstd=17"
    source_dir = "sdbus-cpp"

    def source(self):
        self.run("git clone https://github.com/Kistler-Group/sdbus-cpp.git")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows" and not self.options.shared:
            self.output.warn("Warning! Static builds in Windows are unstable")

    def build_configure(self):
        
        installer = tools.SystemPackageTool()
        installer.install('libsystemd-dev')

        with tools.chdir(os.path.join(self.source_folder, self.source_dir)):
            self.run('./autogen.sh')
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = self.options.fPIC
            with tools.environment_append(env_build.vars):
                # fix rpath
                if self.settings.os == "Macos":
                    tools.replace_in_file("configure", r"-install_name \$rpath/", "-install_name ")
                configure_args = ['--disable-tests']
                if self.options.fPIC:
                    configure_args.extend(['--with-pic'])
                if self.options.shared:
                    configure_args.extend(['--enable-shared', '--disable-static'])
                else:
                    configure_args.extend(['--enable-static', '--disable-shared'])
                env_build.configure(args=configure_args)
                env_build.make()
                env_build.make(args=['install'])

    def build(self):
        self.build_configure()

    def package(self):
        pass


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.cpp_info.libs.append('m')
