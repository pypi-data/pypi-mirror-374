#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "e7-switcher::e7-switcher" for configuration "Release"
set_property(TARGET e7-switcher::e7-switcher APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(e7-switcher::e7-switcher PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libe7-switcher.a"
  )

list(APPEND _cmake_import_check_targets e7-switcher::e7-switcher )
list(APPEND _cmake_import_check_files_for_e7-switcher::e7-switcher "${_IMPORT_PREFIX}/lib/libe7-switcher.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
