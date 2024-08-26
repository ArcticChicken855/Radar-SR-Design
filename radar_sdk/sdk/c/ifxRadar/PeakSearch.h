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
 * @file PeakSearch.h

 * \brief \copybrief gr_peaksearch
 *
 * For details refer to \ref gr_peaksearch
 */

#ifndef IFX_RADAR_PEAK_SEARCH_H
#define IFX_RADAR_PEAK_SEARCH_H

/*
==============================================================================
   1. INCLUDE FILES
==============================================================================
*/

#include "ifxBase/Types.h"
#include "ifxBase/Vector.h"


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
 * @brief Defines the structure for Peak Search module related settings.
 *
 * @image html img_peak_search_module.png "Example showing config params for ifx_peak_search_create (config params in bold)" width=600px
 *
 */
typedef struct
{
    ifx_Float_t value_per_bin;     /**< This is the value quantity 'x' represented by each bin (or each sample) of the input data set.
                                        For e.g., if the input data set is a range spectrum, then this value gives the
                                        range represented by each sample of the data set.*/
    ifx_Float_t search_zone_start; /**< This specifies the start value of a section of the input data where the peak
                                        search needs to be made.
                                        For e.g., if the data set is a range spectrum this value specifies the starting range
                                        value of the search zone.*/
    ifx_Float_t search_zone_end;   /**< This specifies the end value of a section of the input data where the peak
                                        search needs to be made.
                                        For e.g., if the data set is a range spectrum this value specifies the end range
                                        value of the search zone.*/
    ifx_Float_t threshold_factor;  /**< The peak search incorporates an adaptive threshold value of 'y' below which any peaks are
                                        ignored. This factor is multiplied with the mean value of the entire input data set to get
                                        an adaptive threshold value.*/
    ifx_Float_t threshold_offset;  /**< This value is added to the value obtained by multiplying the threshold_factor with
                                        the mean of the data set to get the final 'y' threshold.*/
    uint32_t max_num_peaks;        /**< This decides the max number of peaks to be identified in the search zone.*/
} ifx_Peak_Search_Config_t;

/**
 * @brief Defines the structure for Peak Search module return results.
 */
typedef struct
{
    uint32_t peak_count; /**< Number of found peaks.*/
    uint32_t* index;     /**< Array of indices of found peaks.*/
} ifx_Peak_Search_Result_t;

/**
 * @brief A handle for an instance of Peak Search module, see Peak_Search.h.
 */
typedef struct ifx_Peak_Search_s ifx_Peak_Search_t;

/*
==============================================================================
   4. FUNCTION PROTOTYPES
==============================================================================
*/

/** @addtogroup gr_cat_Radar
 * @{
 */

/** @defgroup gr_peaksearch Peak Search
 * @brief API for Peak Search preprocessing
 *
 * Peak search function searches for peaks inside given
 * data with given conditions.
 *
 * @{
 */

/**
 * @brief Creates a peak search handle with the some input parameters that decide
 *        the nature of the peak search.
 *
 * @image html img_peak_search_module.png "Example showing params from ifx_Peak_Search_Config_t (params in bold)" width=600px
 *
 * @param [in]     config    The peak search settings containing the rules
 *                           on how peak search is applied.
 *
 * @return Handle to the newly created instance or NULL in case of failure.
 *
 */
IFX_DLL_PUBLIC
ifx_Peak_Search_t* ifx_peak_search_create(const ifx_Peak_Search_Config_t* config);

/**
 * @brief Destroys the peak search handle.
 *
 * @param [in,out] handle    A handle to the peak search object
 *
 */
IFX_DLL_PUBLIC
void ifx_peak_search_destroy(ifx_Peak_Search_t* handle);

/**
 * @brief Uses a valid peak search handle to search peaks from input data_set.
 *        The run function looks for peaks in the data_set vector between \ref ifx_Peak_Search_Config_t.search_zone_start
 *        and \ref ifx_Peak_Search_Config_t.search_zone_end, as long as the peak values are higher than a threshold
 *        obtained by multiplying the mean value of the data_set with \ref ifx_Peak_Search_Config_t.threshold_factor and
 *        adding \ref ifx_Peak_Search_Config_t.threshold_offset to it. The peaks are computed by comparing with
 *        2 neighbouring values on either side of every sample value within the search zone.
 *        The peak search stops once the entire search zone has been parsed for peaks OR once
 *        \ref ifx_Peak_Search_Config_t.max_num_peaks are encountered, whichever is earlier.
 *
 * @param [in,out] handle    A handle to the peak search object
 * @param [in]     data_set  The target data set to search for peaks
 * @param [out]    result    Result of the peak search
 *
 */
IFX_DLL_PUBLIC
void ifx_peak_search_run(ifx_Peak_Search_t* handle,
                         const ifx_Vector_R_t* data_set,
                         ifx_Peak_Search_Result_t* result);

/**
 * @}
 */

/**
 * @}
 */

#ifdef __cplusplus
}  // extern "C"
#endif

#endif /* IFX_RADAR_PEAK_SEARCH_H */
