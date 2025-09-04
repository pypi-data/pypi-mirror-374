#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "stempy::stem" for configuration "Release"
set_property(TARGET stempy::stem APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(stempy::stem PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libstem.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libstem.dylib"
  )

list(APPEND _cmake_import_check_targets stempy::stem )
list(APPEND _cmake_import_check_files_for_stempy::stem "${_IMPORT_PREFIX}/lib/libstem.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
