/*
 * NVIDIA_COPYRIGHT_BEGIN
 *
 * Copyright (c) 2022-2025, NVIDIA CORPORATION.  All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 *
 * NVIDIA_COPYRIGHT_END
 */

#ifndef nvJitLink_INCLUDED
#define nvJitLink_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdlib.h>

/**
 *
 * \defgroup error Error codes
 *
 */

/** \ingroup error
 *
 * \brief    The enumerated type nvJitLinkResult defines API call result codes.
 *           nvJitLink APIs return nvJitLinkResult codes to indicate the result.
 */

typedef enum {
  NVJITLINK_SUCCESS = 0,
  NVJITLINK_ERROR_UNRECOGNIZED_OPTION, /**< Unrecognized Option */
  NVJITLINK_ERROR_MISSING_ARCH, /**< Option `-arch=sm_NN` not specified */
  NVJITLINK_ERROR_INVALID_INPUT, /**< Invalid Input */
  NVJITLINK_ERROR_PTX_COMPILE, /**< Issue during PTX Compilation */
  NVJITLINK_ERROR_NVVM_COMPILE, /**< Issue during NVVM Compilation */
  NVJITLINK_ERROR_INTERNAL, /**< Internal Error */
  NVJITLINK_ERROR_THREADPOOL, /**< Issue with Thread Pool */
  NVJITLINK_ERROR_UNRECOGNIZED_INPUT, /**< Unrecognized Input */
  NVJITLINK_ERROR_FINALIZE, /**< Finalizer Error */
  NVJITLINK_ERROR_NULL_INPUT, /**< Null Input */
  NVJITLINK_ERROR_INCOMPATIBLE_OPTIONS, /**< Incompatible Options */
  NVJITLINK_ERROR_INCORRECT_INPUT_TYPE, /**< Incorrect Input Type */
  NVJITLINK_ERROR_ARCH_MISMATCH, /**< Arch Mismatch */
  NVJITLINK_ERROR_OUTDATED_LIBRARY, /**< Outdated Library */
  NVJITLINK_ERROR_MISSING_FATBIN, /**< Missing Fatbin */
  NVJITLINK_ERROR_UNRECOGNIZED_ARCH, /**< Unrecognized -arch value */
  NVJITLINK_ERROR_UNSUPPORTED_ARCH, /**< Unsupported -arch value */
  NVJITLINK_ERROR_LTO_NOT_ENABLED /**< Requires -lto */
} nvJitLinkResult;

/**
 *
 * \defgroup linking Linking
 *
 */

/** \ingroup linking
 *
 * \brief    The enumerated type nvJitLinkInputType defines the kind of inputs
 *           that can be passed to nvJitLinkAdd* APIs.
 */

typedef enum {
  NVJITLINK_INPUT_NONE = 0, /**< Error Type */
  NVJITLINK_INPUT_CUBIN = 1, /**< For CUDA Binaries */
  NVJITLINK_INPUT_PTX, /**< For PTX */
  NVJITLINK_INPUT_LTOIR, /**< For LTO-IR */
  NVJITLINK_INPUT_FATBIN, /**< For Fatbin */
  NVJITLINK_INPUT_OBJECT, /**< For Host Object */
  NVJITLINK_INPUT_LIBRARY, /**< For Host Library */
  NVJITLINK_INPUT_INDEX, /**< For Index File */
  NVJITLINK_INPUT_ANY = 10 /**< Dynamically chooses from the valid types */
} nvJitLinkInputType;

/**
 * \defgroup options Supported Link Options
 *
 * nvJitLink supports the link options below.
 * Option names are prefixed with a single dash (\c -).
 * Options that take a value have an assignment operator (\c =)
 * followed by the option value, with no spaces, e.g. \c "-arch=sm_90".
 *
 * The supported options are:
 * - \c -arch=sm_<N\> \n
 *   Pass SM architecture value.  See nvcc for valid values of <N\>.
 *   Can use compute_<N\> value instead if only generating PTX.
 *   This is a required option.  
 * - \c -maxrregcount=<N\> \n
 *   Maximum register count.
 * - \c -time \n
 *   Print timing information to InfoLog.
 * - \c -verbose \n
 *   Print verbose messages to InfoLog.
 * - \c -lto \n
 *   Do link time optimization.
 * - \c -ptx \n
 *   Emit ptx after linking instead of cubin; only supported with \c -lto
 * - \c -O<N\> \n
 *   Optimization level. Only 0 and 3 are accepted.
 * - \c -g \n
 *   Generate debug information.
 * - \c -lineinfo \n
 *   Generate line information.
 * - \c -ftz=<n\> \n
 *   Flush to zero.
 * - \c -prec-div=<n\> \n
 *   Precise divide.
 * - \c -prec-sqrt=<n\> \n
 *   Precise square root.
 * - \c -fma=<n\> \n
 *   Fast multiply add.
 * - \c -kernels-used=<name\> \n
 *   Pass list of kernels that are used; any not in the list can be removed.
 *   This option can be specified multiple times.
 * - \c -variables-used=<name\> \n
 *   Pass list of variables that are used; any not in the list can be removed.
 *   This option can be specified multiple times.
 * - \c -optimize-unused-variables \n
 *   Normally device code optimization is limited by not knowing what the
 *   host code references.  With this option it can assume that if a variable
 *   is not referenced in device code then it can be removed.
 * - \c -Xptxas=<opt\> \n
 *   Pass <opt\> to ptxas.  This option can be called multiple times.
 * - \c -split-compile=<N\> \n
 *   Split compilation maximum thread count. Use 0 to use all available processors.
 *   Value of 1 disables split compilation (default).
 * - \c -split-compile-extended=<N\> \n
 *   A more aggressive form of split compilation available in LTO mode only.
 *   Accepts a maximum thread count value. Use 0 to use all available processors.
 *   Value of 1 disables extended split compilation (default).
 *   Note: This option can potentially impact performance of the compiled binary.
 * - \c -jump-table-density=<N\> \n
 *   When doing LTO, specify the case density percentage in switch statements,
 *   and use it as a minimal threshold to determine whether jump table(brx.idx 
 *   instruction) will be used to implement a switch statement. Default
 *   value is 101. The percentage ranges from 0 to 101 inclusively.
 * - \c -no-cache \n
 *   Don't cache the intermediate steps of nvJitLink.
 * - \c -device-stack-protector \n
 *   Enable stack canaries in device code.
 *   Stack canaries make it more difficult to exploit certain types of memory safety bugs involving stack-local variables.
 *   The compiler uses heuristics to assess the risk of such a bug in each function.  Only those functions which are deemed high-risk make use of a stack canary.
 */

/**
 * \ingroup linking
 * \brief   nvJitLinkHandle is the unit of linking, and an opaque handle for
 *          a program.
 *
 * To link inputs, an instance of nvJitLinkHandle must be created first with
 * nvJitLinkCreate().
 */

typedef struct nvJitLink* nvJitLinkHandle; // opaque handle

// For versioning we will have separate API version for each library version

extern nvJitLinkResult __nvJitLinkCreate_13_0(
  nvJitLinkHandle *handle,
  uint32_t numOptions,
  const char * const * options);
/**
 * \ingroup linking
 * \brief   nvJitLinkCreate creates an instance of nvJitLinkHandle with the
 *          given input options, and sets the output parameter \p handle.
 *
 * \param   [out] handle       Address of nvJitLink handle.
 * \param   [in]  numOptions   Number of options passed.
 * \param   [in]  options      Array of size \p numOptions of option strings.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_UNRECOGNIZED_OPTION\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_MISSING_ARCH\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * It supports options listed in \ref options.
 *
 * \see nvJitLinkDestroy
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkCreate(
  nvJitLinkHandle *handle,
  uint32_t numOptions,
  const char **options)
{
  return __nvJitLinkCreate_13_0 (handle, numOptions, options);
}
#endif
 
extern nvJitLinkResult __nvJitLinkDestroy_13_0 (nvJitLinkHandle *handle);
/**
 * \ingroup linking
 * \brief   nvJitLinkDestroy frees the memory associated with the given handle
 *          and sets it to NULL.
 *
 * \param    [in] handle      Address of nvJitLink handle.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * \see nvJitLinkCreate
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkDestroy (nvJitLinkHandle *handle)
{
  return __nvJitLinkDestroy_13_0 (handle);
}
#endif
 
extern nvJitLinkResult __nvJitLinkAddData_13_0(
  nvJitLinkHandle handle,
  nvJitLinkInputType inputType,
  const void *data,
  size_t size,
  const char *name); // name can be null
/**
 * \ingroup linking
 * \brief   nvJitLinkAddData adds data image to the link. 
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [in] inputType   kind of input.
 * \param    [in] data        pointer to data image in memory.
 * \param    [in] size        size of the data.
 * \param    [in] name        name of input object.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkAddData(
  nvJitLinkHandle handle,
  nvJitLinkInputType inputType,
  const void *data,
  size_t size,
  const char *name) // name can be null
{
  return __nvJitLinkAddData_13_0 (handle, inputType, data, size, name);
}
#endif
 
extern nvJitLinkResult __nvJitLinkAddFile_13_0(
  nvJitLinkHandle handle,
  nvJitLinkInputType inputType,
  const char *fileName); // includes path to file
/**
 * \ingroup linking
 * \brief   nvJitLinkAddFile reads data from file and links it in. 
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [in] inputType   kind of input.
 * \param    [in] fileName    name of file.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkAddFile(
  nvJitLinkHandle handle,
  nvJitLinkInputType inputType,
  const char *fileName) // includes path to file
{
  return __nvJitLinkAddFile_13_0 (handle, inputType, fileName);
}
#endif
 
extern nvJitLinkResult __nvJitLinkComplete_13_0 (nvJitLinkHandle handle);
/**
 * \ingroup linking
 * \brief   nvJitLinkComplete does the actual link. 
 *
 * \param    [in] handle      nvJitLink handle.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkComplete (nvJitLinkHandle handle)
{
  return __nvJitLinkComplete_13_0 (handle);
}
#endif
 
extern nvJitLinkResult __nvJitLinkGetLinkedCubinSize_13_0(
  nvJitLinkHandle handle,
  size_t *size);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetLinkedCubinSize gets the size of the linked cubin.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] size       Size of the linked cubin.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * \see nvJitLinkGetLinkedCubin
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetLinkedCubinSize(
  nvJitLinkHandle handle,
  size_t *size)
{
  return __nvJitLinkGetLinkedCubinSize_13_0 (handle, size);
}
#endif

extern nvJitLinkResult __nvJitLinkGetLinkedCubin_13_0(
  nvJitLinkHandle handle,
  void *cubin);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetLinkedCubin gets the linked cubin.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] cubin      The linked cubin.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * User is responsible for allocating enough space to hold the \p cubin.
 * \see nvJitLinkGetLinkedCubinSize
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetLinkedCubin(
  nvJitLinkHandle handle,
  void *cubin)
{
  return __nvJitLinkGetLinkedCubin_13_0 (handle, cubin);
}
#endif
 
extern nvJitLinkResult __nvJitLinkGetLinkedPtxSize_13_0(
  nvJitLinkHandle handle,
  size_t *size);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetLinkedPtxSize gets the size of the linked ptx.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] size       Size of the linked PTX.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * Linked PTX is only available when using the \c -lto option.
 * \see nvJitLinkGetLinkedPtx
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetLinkedPtxSize(
  nvJitLinkHandle handle,
  size_t *size)
{
  return __nvJitLinkGetLinkedPtxSize_13_0 (handle, size);
}
#endif

extern nvJitLinkResult __nvJitLinkGetLinkedPtx_13_0(
  nvJitLinkHandle handle,
  char *ptx);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetLinkedPtx gets the linked ptx.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] ptx        The linked PTX.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * Linked PTX is only available when using the \c -lto option.
 * User is responsible for allocating enough space to hold the \p ptx.
 * \see nvJitLinkGetLinkedPtxSize
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetLinkedPtx(
  nvJitLinkHandle handle,
  char *ptx)
{
  return __nvJitLinkGetLinkedPtx_13_0 (handle, ptx);
}
#endif
 
extern nvJitLinkResult __nvJitLinkGetErrorLogSize_13_0(
  nvJitLinkHandle handle,
  size_t *size);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetErrorLogSize gets the size of the error log.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] size       Size of the error log.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * \see nvJitLinkGetErrorLog
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetErrorLogSize(
  nvJitLinkHandle handle,
  size_t *size)
{
  return __nvJitLinkGetErrorLogSize_13_0 (handle, size);
}
#endif

extern nvJitLinkResult __nvJitLinkGetErrorLog_13_0(
  nvJitLinkHandle handle,
  char *log);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetErrorLog puts any error messages in the log.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] log        The error log.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * User is responsible for allocating enough space to hold the \p log.
 * \see nvJitLinkGetErrorLogSize
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetErrorLog(
  nvJitLinkHandle handle,
  char *log)
{
  return __nvJitLinkGetErrorLog_13_0 (handle, log);
}
#endif

extern nvJitLinkResult __nvJitLinkGetInfoLogSize_13_0(
  nvJitLinkHandle handle,
  size_t *size);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetInfoLogSize gets the size of the info log.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] size       Size of the info log.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * \see nvJitLinkGetInfoLog
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetInfoLogSize(
  nvJitLinkHandle handle,
  size_t *size)
{
  return __nvJitLinkGetInfoLogSize_13_0 (handle, size);
}
#endif

extern nvJitLinkResult __nvJitLinkGetInfoLog_13_0(
  nvJitLinkHandle handle,
  char *log);
/**
 * \ingroup linking
 * \brief   nvJitLinkGetInfoLog puts any info messages in the log.
 *
 * \param    [in] handle      nvJitLink handle.
 * \param    [out] log        The info log.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 * User is responsible for allocating enough space to hold the \p log.
 * \see nvJitLinkGetInfoLogSize
 */
#ifndef NVJITLINK_NO_INLINE
static inline nvJitLinkResult nvJitLinkGetInfoLog(
  nvJitLinkHandle handle,
  char *log)
{
  return __nvJitLinkGetInfoLog_13_0 (handle, log);
}
#endif

/**
 * \ingroup linking
 * \brief   nvJitLinkVersion returns the current version of nvJitLink.
 *
 * \param    [out] major        The major version.
 * \param    [out] minor        The minor version.
 * \return
 *   - \link #nvJitLinkResult NVJITLINK_SUCCESS \endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INVALID_INPUT\endlink
 *   - \link #nvJitLinkResult NVJITLINK_ERROR_INTERNAL\endlink
 *
 */
extern nvJitLinkResult nvJitLinkVersion(
  unsigned int *major,
  unsigned int *minor);

#ifdef __cplusplus
}
#endif

#endif // nvJitLink_INCLUDED

