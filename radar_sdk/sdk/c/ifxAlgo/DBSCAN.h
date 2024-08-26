/* ===========================================================================
** Copyright (C) 2021 Infineon Technologies AG
**
** Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are met:
**
** 1. Redistributions of source code must retain the above copyright notice,
**    this list of conditions and the following disclaimer.
** 2. Redistributions in binary form must reproduce the above copyright
**    notice, this list of conditions and the following disclaimer in the
**    documentation and/or other materials provided with the distribution.
** 3. Neither the name of the copyright holder nor the names of its
**    contributors may be used to endorse or promote products derived from
**    this software without specific prior written permission.
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
** AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
** IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
** ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
** LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
** CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
** SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
** INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
** CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
** ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
** POSSIBILITY OF SUCH DAMAGE.
** ===========================================================================
*/

/**
 * @file DBSCAN.h
 *
 * \brief \copybrief gr_dbscan
 *
 * For details refer to \ref gr_dbscan
 */

#ifndef IFX_ALGO_DBSCAN_H
#define IFX_ALGO_DBSCAN_H

/*
==============================================================================
   1. INCLUDE FILES
==============================================================================
*/

#include "ifxBase/Types.h"


#ifdef __cplusplus
extern "C"
{
#endif


/*
==============================================================================
   2. DEFINITIONS
==============================================================================
*/

/*
==============================================================================
   3. TYPES
==============================================================================
*/

/**
 * @brief A handle for an instance of DBSCAN module, see DBSCAN.h
 */
typedef struct ifx_DBSCAN_s ifx_DBSCAN_t;

/**
 * @brief Defines the structure for DBSCAN module related settings.
 */
typedef struct
{
    uint8_t min_points;          /**< Minimum number of neighbor points to be recognized as a cluster.*/
    ifx_Float_t min_dist;        /**< Minimum distance at which a point is recognized as a neighbor.*/
    uint32_t max_num_detections; /**< Maximum number of detections (points) which can appear.*/
} ifx_DBSCAN_Config_t;


/*
==============================================================================
   4. FUNCTION PROTOTYPES
==============================================================================
*/

/** @addtogroup gr_cat_Algorithms
 * @{
 */

/** @defgroup gr_dbscan DBSCAN
 * @brief API for Density-based spatial clustering of applications with noise (DBSCAN) algorithm
 *
 * This algorithm is used to perform Density-based spatial clustering
 * of applications with noise (DBSCAN).
 *
 * @if ssct_radarsdk_algorithms_detect_dbscan
 * An algorithm explanation is available at the \ref ssct_radarsdk_algorithms_detect_dbscan SDK documentation.
 * @endif
 *
 * @{
 */

/**
 * @brief Creates an instance of the DBSCAN handle with given configuration.
 *
 * @param [in]     config    Configuration options of the DBSCAN object.
 *
 * @return  Handle to the newly created instance or NULL in case of failure.
 *
 */
IFX_DLL_PUBLIC
ifx_DBSCAN_t* ifx_dbscan_create(const ifx_DBSCAN_Config_t* config);

/**
 * @brief Releases all resources held by the given handle.
 *
 * @param [in,out] handle    A handle to the DBSCAN object.
 *
 */
IFX_DLL_PUBLIC
void ifx_dbscan_destroy(ifx_DBSCAN_t* handle);

/**
 * @brief Performs the DBSCAN (Density-based spatial clustering of applications with noise)
 * algorithm on given detections.
 *
 * @param [in]     handle              A handle to the DBSCAN object.
 * @param [in]     detections          The detection points to search for clusters in. Note that detections
 *                                     must store the coordinates interleaved (x1, y1, x2, y2,..., xn, yn).
 *                                     Therefore this parameter must point to valid memory of the size
 *                                     2 * num_detections * sizeof(type).
 * @param [in]     num_detections      Number of detection points.
 * @param [out]    cluster_vector      The output vector will consist the vector number for each detection.
 *                                     This vector must point to valid memory of minimum num_detection elements.
 */
IFX_DLL_PUBLIC
void ifx_dbscan_run(ifx_DBSCAN_t* handle,
                    const uint16_t* detections,
                    uint16_t num_detections,
                    uint16_t* cluster_vector);

/**
 * @brief Sets the min points attribute see \ref ifx_DBSCAN_Config_t.
 *
 * @param [in]     handle              A handle to the DBSCAN object.
 * @param [in]     min_points          The minimum points to set.
 *
 */
IFX_DLL_PUBLIC
void ifx_dbscan_set_min_points(ifx_DBSCAN_t* handle,
                               uint16_t min_points);

/**
 * @brief Sets the min distance attribute see \ref ifx_DBSCAN_Config_t.
 *
 * @param [in]     handle              A handle to the DBSCAN object.
 * @param [in]     min_distance        The minimum distance to set.
 *
 */
IFX_DLL_PUBLIC
void ifx_dbscan_set_min_distance(ifx_DBSCAN_t* handle,
                                 ifx_Float_t min_distance);

/**
 * @}
 */

/**
 * @}
 */

#ifdef __cplusplus
}  // extern "C"
#endif

#endif /* IFX_ALGO_DBSCAN_H */
