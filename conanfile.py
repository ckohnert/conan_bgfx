from conans import ConanFile, tools
import shutil
import sys
import os
import multiprocessing


class bgfxConan(ConanFile):
	name = "bgfx"
	version = "1.0"
	license = "BSD-2"
	
	url = "https://github.com/bkaradzic/bgfx"
	
	options = {
		"shared" : [True, False]
	}
	
	default_options = "shared=False"
	
	settings = {
		"os" : None,
		"compiler": None,
#			"Visual Studio": {"version":[9, 10, 11, 12, 14]}
		"build_type": ["Debug", "Release"],
		"arch" : ["x86", "x86_64"]
	}
	
	def _fetch_zip(self, url, final_name):
		
		# Split the filename part off of "https://.../foo-master.zip"
		(dirname, filename) = os.path.split(url)
		if url.startswith("file://"):
			shutil.copy(url[7:], filename)
		else:
			tools.download(url, filename)
		tools.unzip(filename)
		shutil.move(filename.replace(".zip", ""), final_name)
		os.unlink(filename)
		
	

	def source(self):
		# If there's an official release, we could clone it directly, for now we
		# just grab master...
		
		#self.run("git clone https://github.com/bkaradzic/bx")
		#self.run("git clone https://github.com/bkaradzic/bgfx")
		self._fetch_zip("https://github.com/bkaradzic/bx/archive/master.zip", "bx")
		self._fetch_zip("https://github.com/bkaradzic/bgfx/archive/master.zip", "bgfx")
		# BGFX includes a couple helper binaries in its distro, that don't have proper
		# execute flags if unzipped.
		if tools.os_info.is_linux or tools.os_info.is_macos:
			self.run("chmod 755 bx/tools/bin/*/*")
		

	def system_requirements(self):
	
		if self.settings.os == "Linux":
			pkgtool = tools.SystemPackageTool()
			pkgtool.update()
			pkgtool.install("libgl1-mesa-dev")
			pkgtool.install("x11proto-core-dev")
			pkgtool.install("libx11-dev")

		
	def build(self):
	
		target = ""
		dist_target = ""
		build_type = "release" if self.settings.build_type == "Release" else "debug"
		arch = 32 if self.settings.arch == "x86" else 64
			
		if self.settings.os == "Windows":

			# TODO: Windows is completely untested currently...
			if self.settings.compiler == "Visual Studio":
				v = self.settings.compiler.version
				vsremap = {
					"9":  "vs2008",
					"10": "vs2010",
					"11": "vs2012",
					"12": "vs2013",
					"14": "vs2015"
				}
				target = "%s-%s%d" % (vsremap[v], build_type, arch)

			elif self.settings.compiler == "gcc" or self.settings.compiler == "clang":
			
				target = "mingw-%s-%s%d" % (
					self.settings.compiler,
					build_type,
					arch)
			
			dist_target = "dist-windows"
		
		elif self.settings.os == "Macos":
		
			target = "osx-%s%d" % (
				build_type,
				arch)
			dist_target = "dist-darwin"
		
		elif self.settings.os == "Linux":
			
			target = "linux-%s%d" % (
				build_type,
				arch)
			dist_target = "dist-linux"
		
		if target == "":
			print "******************************************************************************************"
			print " Package does not support the specified platform. Feel free to contribute"
			print " additional platform support."
			print "   OS:", self.settings.os
			print "   Compiler:", self.settings.compiler
			print "   Arch:", self.settings.arch
			print "******************************************************************************************"
			sys.exit(1)

		self.run("cd bgfx && make -j %d %s && make %s" % (multiprocessing.cpu_count(), target, dist_target))
		

	def package(self):
		if self.settings.os == "Windows":
		
			self.copy("*", dst="bin", src="bgfx/tools/bin/windows")
			if self.settings.arch == "x86":
				self.copy("*bgfx*", dst="lib32", src="bgfx/.build/win32_mingw-gcc/bin")
			else:
				self.copy("*bgfx*", dst="lib64", src="bgfx/.build/win64_mingw-gcc/bin")
			
		elif self.settings.os == "Linux":
		
			self.copy("*", dst="bin", src="bgfx/tools/bin/linux")
			if self.settings.arch == "x86":
				self.copy("*bgfx*", dst="lib32", src="bgfx/.build/linux32_gcc/bin")
			else:
				self.copy("*bgfx*", dst="lib64", src="bgfx/.build/linux64_gcc/bin")
			
		elif self.settings.os == "Macos":
		
			self.copy("*", dst="bin", src="bgfx/tools/bin/darwin")
			if self.settings.arch == "x86":
				self.copy("*bgfx*", dst="lib32", src="bgfx/.build/osx32_clang/bin")
			else:
				self.copy("*bgfx*", dst="lib64", src="bgfx/.build/osx64_clang/bin")
		
		self.copy("*.h", dst="include", src="bgfx/include")
		self.copy("*.h", dst="3rdparty", src="bgfx/3rdparty")
		
		

	def package_info(self):
		self.cpp_info.includedirs.append("3rdparty")

		if self.options.shared:
			libname = "bgfx-shared-lib%s" % self.settings.build_type
		else:
			libname = "bgfx%s" % self.settings.build_type
		
		if self.settings.arch == "x86":
			self.cpp_info.libdirs = ["lib32"]
		else:
			self.cpp_info.libdirs = ["lib64"]
		
		if self.settings.os == "Linux":
	
			self.cpp_info.libs = ["m", "dl", "pthread", "X11", "GL"]
	
			if self.options.shared:
				self.cpp_info.libs.append(libname)
			else:
				self.cpp_info.libs.append("%s.a" % libname)
			
		elif self.settings.os == "Windows":
	
			# what's the linking syntax for windows?
			self.cpp_info.libs = ["GL", libname ]
	
		elif self.settings.os == "Macos":
	
			if self.options.shared:
				self.cpp_info.libs.append(libname)
			else:
				self.cpp_info.libs.append("%s.a" % libname)
			self.cpp_info.sharedlinkflags = ["-framework OpenGL -framework Cocoa -framework QuartzCore -weak_framework Metal"]
			self.cpp_info.exelinkflags = self.cpp_info.sharedlinkflags
			
		
		