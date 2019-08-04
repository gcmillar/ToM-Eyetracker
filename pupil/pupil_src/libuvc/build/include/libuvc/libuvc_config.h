#ifndef LIBUVC_CONFIG_H
#define LIBUVC_CONFIG_H

#define LIBUVC_VERSION_MAJOR 0
#define LIBUVC_VERSION_MINOR 0
#define LIBUVC_VERSION_PATCH 9
#define LIBUVC_VERSION_STR "0.0.9"
#define LIBUVC_VERSION_INT                      \
  ((0 << 16) |             \
   (0 << 8) |              \
   (9))

/** @brief Test whether libuvc is new enough
 * This macro evaluates true iff the current version is
 * at least as new as the version specified.
 */
#define LIBUVC_VERSION_GTE(major, minor, patch)                         \
  (LIBUVC_VERSION_INT >= (((major) << 16) | ((minor) << 8) | (patch)))

/* #undef LIBUVC_HAS_JPEG */

#endif // !def(LIBUVC_CONFIG_H)
