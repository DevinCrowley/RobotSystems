# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.10

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/ubuntu/armpi_fpv/src

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/ubuntu/armpi_fpv/build

# Utility rule file for lab_config_geneus.

# Include the progress variables for this target.
include lab_config/CMakeFiles/lab_config_geneus.dir/progress.make

lab_config_geneus: lab_config/CMakeFiles/lab_config_geneus.dir/build.make

.PHONY : lab_config_geneus

# Rule to build all files generated by this target.
lab_config/CMakeFiles/lab_config_geneus.dir/build: lab_config_geneus

.PHONY : lab_config/CMakeFiles/lab_config_geneus.dir/build

lab_config/CMakeFiles/lab_config_geneus.dir/clean:
	cd /home/ubuntu/armpi_fpv/build/lab_config && $(CMAKE_COMMAND) -P CMakeFiles/lab_config_geneus.dir/cmake_clean.cmake
.PHONY : lab_config/CMakeFiles/lab_config_geneus.dir/clean

lab_config/CMakeFiles/lab_config_geneus.dir/depend:
	cd /home/ubuntu/armpi_fpv/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/ubuntu/armpi_fpv/src /home/ubuntu/armpi_fpv/src/lab_config /home/ubuntu/armpi_fpv/build /home/ubuntu/armpi_fpv/build/lab_config /home/ubuntu/armpi_fpv/build/lab_config/CMakeFiles/lab_config_geneus.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : lab_config/CMakeFiles/lab_config_geneus.dir/depend

