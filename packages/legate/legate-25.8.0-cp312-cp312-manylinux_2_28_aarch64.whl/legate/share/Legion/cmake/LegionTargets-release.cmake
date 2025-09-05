#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Legion::RealmRuntime" for configuration "Release"
set_property(TARGET Legion::RealmRuntime APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Legion::RealmRuntime PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "ucc::ucc"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/librealm-legate.so.1"
  IMPORTED_SONAME_RELEASE "librealm-legate.so.1"
  )

list(APPEND _cmake_import_check_targets Legion::RealmRuntime )
list(APPEND _cmake_import_check_files_for_Legion::RealmRuntime "${_IMPORT_PREFIX}/lib64/librealm-legate.so.1" )

# Import target "Legion::LegionRuntime" for configuration "Release"
set_property(TARGET Legion::LegionRuntime APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(Legion::LegionRuntime PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib64/liblegion-legate.so.1"
  IMPORTED_SONAME_RELEASE "liblegion-legate.so.1"
  )

list(APPEND _cmake_import_check_targets Legion::LegionRuntime )
list(APPEND _cmake_import_check_files_for_Legion::LegionRuntime "${_IMPORT_PREFIX}/lib64/liblegion-legate.so.1" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
