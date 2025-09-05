// -*- mode: fundamental-mode  -*-
/*
 * SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <legion_defines.h>
#include <realm_defines.h>

#include <legate/version.h>

#ifndef LEGION_REDOP_HALF
#error "Legate needs Legion to be compiled with -DLEGION_REDOP_HALF"
#endif

/* #undef LEGATE_USE_DEBUG */

/* #undef LEGATE_USE_CUDA */

/* #undef LEGATE_USE_NETWORK */

/* #undef LEGATE_USE_OPENMP */

/* #undef LEGATE_USE_CAL */

/* #undef LEGATE_USE_HDF5 */

/* #undef LEGATE_USE_HDF5_VFD_GDS */

/* #undef LEGATE_USE_NCCL */

/*
 * TODO(amberhassaan): Remove this flag when
 * https://github.com/nv-legate/cupynumeric.internal/issues/703
 * is resolved
 */
/* #undef LEGATE_ENABLE_INVERT_DIMS */

#define LEGATE_SHARED_LIBRARY_SUFFIX ".dylib"

#define LEGATE_SHARED_LIBRARY_PREFIX "lib"

#define LEGATE_CONFIGURE_OPTIONS "<unknown configure options>"

#if !defined(LEGATE_USE_OPENMP) && defined(REALM_USE_OPENMP)
#define LEGATE_USE_OPENMP 1
#endif

#ifndef LEGATE_USE_NETWORK
#if defined(REALM_USE_GASNET1) || defined(REALM_USE_GASNETEX) || defined(REALM_USE_MPI) || \
  defined(REALM_USE_UCX)
#define LEGATE_USE_NETWORK 1
#endif
#endif

#ifdef LEGATE_USE_DEBUG
#ifndef CCCL_ENABLE_ASSERTIONS
#define CCCL_ENABLE_ASSERTIONS 1
#endif
#endif

#ifdef LEGION_BOUNDS_CHECKS
#define LEGATE_BOUNDS_CHECKS 1
#endif

#define LEGATE_MAX_DIM LEGION_MAX_DIM

#define LEGATE_MAX_NUM_PROCS LEGION_MAX_NUM_PROCS

#ifdef DOXYGEN
#define LEGATE_DOXYGEN 1
#else
#define LEGATE_DOXYGEN 0
#endif

#if defined(__APPLE__)
#define LEGATE_MACOS 1
#elif defined(__linux__)
#define LEGATE_LINUX 1
#else
#error "Unsupported platform. Please open an issue at https://github.com/nv-legate/legate describing your system"
#endif

#ifndef LEGATE_MACOS
#define LEGATE_MACOS 0
#endif

#ifndef LEGATE_LINUX
#define LEGATE_LINUX 0
#endif

// Cython does not define a "standard" way of detecting cythonized source compilation, so we
// just check for any one of these macros which I found to be defined in the preamble on my
// machine. We need to check enough of them in case the Cython devs ever decide to change one
// of their names to keep our bases covered.
#if defined(CYTHON_HEX_VERSION) || defined(CYTHON_ABI) || defined(CYTHON_INLINE) ||         \
  defined(CYTHON_RESTRICT) || defined(CYTHON_UNUSED) || defined(CYTHON_USE_CPP_STD_MOVE) || \
  defined(CYTHON_FALLTHROUGH)
#define LEGATE_CYTHON 1
#define LEGATE_DEFAULT_WHEN_CYTHON default
#else
#define LEGATE_CYTHON 0
#define LEGATE_DEFAULT_WHEN_CYTHON delete
#endif

// The order of these checks is deliberate. Also the fact that they are one unbroken set of if
// -> elif -> endif. For example, clang defines both __clang__ and __GNUC__ so in order to
// detect the actual GCC, we must catch clang first.
#if defined(__NVCC__)
#define LEGATE_NVCC 1
#elif defined(__NVCOMPILER)
#define LEGATE_NVHPC 1
#elif defined(__EDG__)
#define LEGATE_EDG 1
#elif defined(__clang__)
#define LEGATE_CLANG 1
#elif defined(__GNUC__)
#define LEGATE_GCC 1
#elif defined(_MSC_VER)
#define LEGATE_MSVC 1
#endif

#ifndef LEGATE_NVCC
#define LEGATE_NVCC 0
#endif
#ifndef LEGATE_NVHPC
#define LEGATE_NVHPC 0
#endif
#ifndef LEGATE_EDG
#define LEGATE_EDG 0
#endif
#ifndef LEGATE_CLANG
#define LEGATE_CLANG 0
#endif
#ifndef LEGATE_GCC
#define LEGATE_GCC 0
#endif
#ifndef LEGATE_MSVC
#define LEGATE_MSVC 0
#endif

#ifdef __CUDA_ARCH__
#define LEGATE_DEVICE_COMPILE 1
#else
#define LEGATE_DEVICE_COMPILE 0
#endif

#define LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND() \
  static_assert(true, "see https://stackoverflow.com/a/59153563")

// Since we cannot rely on LEGATE_STRINGIZE_() to be defined
#define LEGATE_PRIVATE_STRINGIZE_(...) #__VA_ARGS__

#define LEGATE_PRAGMA(...) \
  _Pragma(LEGATE_PRIVATE_STRINGIZE_(__VA_ARGS__)) LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND()

#if LEGATE_NVCC
#define LEGATE_PRAGMA_PUSH() LEGATE_PRAGMA(nv_diagnostic push)
#define LEGATE_PRAGMA_POP() LEGATE_PRAGMA(nv_diagnostic pop)
#define LEGATE_PRAGMA_EDG_IGNORE(...) LEGATE_PRAGMA(nv_diag_suppress __VA_ARGS__)
#elif LEGATE_NVHPC || LEGATE_EDG
#define LEGATE_PRAGMA_PUSH() \
  LEGATE_PRAGMA(diagnostic push); LEGATE_PRAGMA_EDG_IGNORE(invalid_error_number)
#define LEGATE_PRAGMA_POP() LEGATE_PRAGMA(diagnostic pop)
#define LEGATE_PRAGMA_EDG_IGNORE(...) LEGATE_PRAGMA(diag_suppress __VA_ARGS__)
#elif LEGATE_CLANG || LEGATE_GCC
#define LEGATE_PRAGMA_PUSH() LEGATE_PRAGMA(GCC diagnostic push)
#define LEGATE_PRAGMA_POP() LEGATE_PRAGMA(GCC diagnostic pop)
#define LEGATE_PRAGMA_GNU_IGNORE(...) LEGATE_PRAGMA(GCC diagnostic ignored __VA_ARGS__)
#endif

#ifndef LEGATE_PRAGMA_PUSH
#define LEGATE_PRAGMA_PUSH() LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND()
#endif

#ifndef LEGATE_PRAGMA_POP
#define LEGATE_PRAGMA_POP() LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND()
#endif

#ifndef LEGATE_PRAGMA_EDG_IGNORE
#define LEGATE_PRAGMA_EDG_IGNORE(...) LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND()
#endif
#ifndef LEGATE_PRAGMA_GNU_IGNORE
#define LEGATE_PRAGMA_GNU_IGNORE(...) LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND()
#endif

#if LEGATE_GCC && !LEGATE_CLANG
#define LEGATE_PRAGMA_GCC_IGNORE(...) LEGATE_PRAGMA_GNU_IGNORE(__VA_ARGS__)
#else
#define LEGATE_PRAGMA_GCC_IGNORE(...) LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND()
#endif

#if LEGATE_CLANG
#define LEGATE_PRAGMA_CLANG_IGNORE(...) LEGATE_PRAGMA_GNU_IGNORE(__VA_ARGS__)
#else
#define LEGATE_PRAGMA_CLANG_IGNORE(...) LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND()
#endif

#if LEGATE_CLANG || LEGATE_GCC
// Don't use LEGATE_PRAGMA here because we can't use LEGATE_WPEDANTIC_SEMICOLON_WORKAROUND for
// it since this must appear after macro uses, which may happen in preprocessor statements
#define LEGATE_DEPRECATED_MACRO_(...) _Pragma(LEGATE_PRIVATE_STRINGIZE_(__VA_ARGS__))
#define LEGATE_DEPRECATED_MACRO(...) \
  LEGATE_DEPRECATED_MACRO_(GCC warning LEGATE_PRIVATE_STRINGIZE_(This macro is deprecated : __VA_ARGS__))
#else
#define LEGATE_DEPRECATED_MACRO(...)
#endif

#ifdef __CUDACC__
#define LEGATE_HOST __host__
#define LEGATE_DEVICE __device__
#define LEGATE_KERNEL __global__
#else
#define LEGATE_HOST
#define LEGATE_DEVICE
#define LEGATE_KERNEL
#endif

#define LEGATE_HOST_DEVICE LEGATE_HOST LEGATE_DEVICE

#ifndef __has_feature
#define __has_feature(x) 0
#endif

#ifndef __has_builtin
#define __has_builtin(x) 0
#endif

#ifndef __has_cpp_attribute
#define __has_cpp_attribute(x) 0
#endif

// __has_feature(thread_sanitizer) is available only on Clang, while GCC defines
// __SANITIZE_THREAD__
#if __has_feature(thread_sanitizer) || defined(__SANITIZE_THREAD__)
#define LEGATE_HAS_TSAN 1
#else
#define LEGATE_HAS_TSAN 0
#endif

// __has_feature(address_sanitizer) is available only on Clang, while GCC defines
// __SANITIZE_ADDRESS__
#if __has_feature(address_sanitizer) || defined(__SANITIZE_ADDRESS__)
#define LEGATE_HAS_ASAN 1
#else
#define LEGATE_HAS_ASAN 0
#endif

namespace legate {

extern const char *const LEGATE_GIT_HASH;
extern const char *const LEGION_GIT_HASH;

} // namespace legate
