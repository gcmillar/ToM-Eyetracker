#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "uvc" for configuration "Release"
set_property(TARGET uvc APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(uvc PROPERTIES
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "-L/usr/local/Cellar/libusb/1.0.22/lib;usb-1.0"
  IMPORTED_LOCATION_RELEASE "/usr/local/lib/libuvc.0.0.9.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libuvc.0.dylib"
  )

list(APPEND _IMPORT_CHECK_TARGETS uvc )
list(APPEND _IMPORT_CHECK_FILES_FOR_uvc "/usr/local/lib/libuvc.0.0.9.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
