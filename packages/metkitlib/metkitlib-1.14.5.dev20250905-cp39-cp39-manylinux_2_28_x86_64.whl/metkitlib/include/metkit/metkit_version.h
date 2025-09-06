#ifndef metkit_version_h
#define metkit_version_h

#define metkit_VERSION_STR "1.14.5.dev20250905"
#define metkit_VERSION     "1.14.5"

#define metkit_VERSION_MAJOR 1
#define metkit_VERSION_MINOR 14
#define metkit_VERSION_PATCH 5

#define metkit_GIT_SHA1 "736ce0dfcf8ea9c23a16a90852f9a860559a7686"

#ifdef __cplusplus
extern "C" {
#endif

const char * metkit_version();

unsigned int metkit_version_int();

const char * metkit_version_str();

const char * metkit_git_sha1();

#ifdef __cplusplus
}
#endif


#endif // metkit_version_h
