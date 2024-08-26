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
 * @file RangeSpectrum.h
 *
 * \brief \copybrief gr_rs
 *
 * For details refer to \ref gr_rs
 */

#ifndef IFX_RADAR_RANGE_SPECTRUM_H
#define IFX_RADAR_RANGE_SPECTRUM_H

/*
==============================================================================
   1. INCLUDE FILES
==============================================================================
*/

#include "ifxAlgo/PreprocessedFFT.h"
#include "ifxAlgo/Window.h"

#include "ifxBase/Matrix.h"
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
 * @brief A handle for an instance of Range Spectrum module, see RangeSpectrum.h
 */
typedef struct ifx_RS_s ifx_RS_t;

/**
 * @brief This enumeration type lists supported modes of range spectrum.
 */
typedef enum
{
    /** The range spectrum is calculated just for one specified chirp in a frame.
     *  @image html img_radar_spectrum_mode_single_chirp.png "Flow - IFX_RS_MODE_SINGLE_CHIRP" width=600px */
    IFX_RS_MODE_SINGLE_CHIRP = 0U,

    /** The range spectrum is calculated as a coherent integration of all chirps in a frame.
     *  @image html img_radar_spectrum_mode_coherent_integration.png "Flow - IFX_RS_MODE_COHERENT_INTEGRATION" width=600px */
    IFX_RS_MODE_COHERENT_INTEGRATION = 1U,

    /** The range spectrum is calculated for one chirp that is identified to have the maximum energy.
     *  @image html img_radar_spectrum_mode_max_energy.png "Flow - IFX_RS_MODE_MAX_ENERGY" width=600px */
    IFX_RS_MODE_MAX_ENERGY = 2U,

    /** The range spectrum will be calculated for every chirp, the maximum bin per column is considered. */
    IFX_RS_MODE_MAX_BIN = 3U
} ifx_RS_Mode_t;

/**
 * @brief Defines the structure for range spectrum related settings. Default mode is \ref IFX_RS_MODE_COHERENT_INTEGRATION
 * if number of chirps is greater than one else it is \ref IFX_RS_MODE_SINGLE_CHIRP
 */
typedef struct
{
    ifx_Float_t spect_threshold;             /**< Threshold is in always linear scale, should be greater than 1e-6.
                                                  Range spectrum output values below this are set to 1e-6 (-120dB).*/
    ifx_Math_Scale_Type_t output_scale_type; /**< Linear or dB scale for the output of range spectrum module.*/
    ifx_PPFFT_Config_t fft_config;           /**< Preprocessed FFT settings for range FFT e.g. mean removal, FFT settings.*/
    uint32_t num_of_chirps_per_frame;        /**< Non-zero positive number with an upper limit not defined yet.*/

} ifx_RS_Config_t;

/*
==============================================================================
   4. FUNCTION PROTOTYPES
==============================================================================
*/

/** @addtogroup gr_cat_Radar
 * @{
 */

/** @defgroup gr_rs Range Spectrum
 * @brief API for Range Spectrum
 *
 * Range spectrum is a 1D FFT transform of time domain data over chirps (also known as Fast time).
 * Here spectrum means, a vector of real absolute amplitude values calculated from complex FFT output.
 * Following signal processing blocks are used for range spectrum;
 *
 * Raw ADC data --> Mean Removal (optional) --> Windowing --> FFT --> Absolute --> thresholding (Linear) --> Scale (Linear or dB)
 *
 * This ifxRadar_RangeSpectrum module defines an API to create & destroy Range spectrum object (handle) and
 * to compute range spectrum along with some helper setter/getter functions to modify few parameters without
 * destroying and recreating range spectrum handle.
 *
 * Range spectrum format without FFT shift:
 *
 * DC bin --> Positive Half --> Negative half
 *
 * Range spectrum format with FFT shift:
 *
 * Negative half --> DC bin --> Positive Half
 *
 * @{
 */

/**
 * @brief Creates a range spectrum handle.
 *
 * Creates a range spectrum handle (object) based on the provided configuration,
 * e.g. number of chirps per frame, samples per chirp (defines zero padding), mean removal flag, window settings,
 * FFT type (\ref ifx_FFT_Type_t) and FFT size. This handle also contains
 * a FFT handle (R2C or C2C) for computing the FFT, temporary memories to compute intermediate results etc.
 *
 * During this handle creation, two cases have been taken into the consideration, regarding the nature of the
 * input from sensor and is defined by \ref ifx_FFT_Type_t,
 * 1. Real input data defined by IFX_FFT_TYPE_R2C
 * 2. Complex input data defined by IFX_FFT_TYPE_C2C
 * In case 1, a special handle has been used to make FFT operation twice faster and memory efficient.
 * However, it is important to use the correct spectrum run function \ref ifx_rs_run_r or
 * \ref ifx_rs_run_cr with the correct handle created based on input data type \ref ifx_FFT_Type_t.
 *
 * Input parameter samples_per_chirp is used to set the zero padding length in the FFT handle because
 * for input data length less than the FFT size, zero padding is required. Thus, if user wants
 * feed the input length different to this parameter, he/she needs to destroy the Range Spectrum handle
 * (using \ref ifx_rs_destroy) and create a new one!
 * Error is returned if any of the parameter is not in the defined range of this enumeration
 * (\ref ifx_FFT_Type_t).
 *
 * Threshold:
 *  - output of range spectrum module below this threshold is clipped to 1e-6 (-120dB).
 * Scale type:
 *  - convert output to dB scale or keep linear scale.
 * Chirp bandwidth:
 *  - is the difference between min freq and max freq in the chirp is used
 * to calculate the semantics of the range axis in the output range spectrum.
 *
 * @param [in]     config    Contains configuration options for range spectrum module
 *
 * @return Handle to the newly created instance or NULL in case of failure.
 *
 */
IFX_DLL_PUBLIC
ifx_RS_t* ifx_rs_create(const ifx_RS_Config_t* config);

/**
 * @brief Performs destruction of range spectrum handle (object) to clear internal
 *        states and memories used for range spectrum calculation.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_destroy(ifx_RS_t* handle);

/**
 * @brief Performs signal processing on a real input I or Q (e.g. mean removal, windowing, zero padding,
 *        FFT transform) and produces a real amplitude spectrum of FFT size as output.
 *        Here, second half of the spectrum is of no use as it is symmetric for real input FFT.
 *
 * The matrix input must have num_chirps_per_frame of rows and num_samples_per_chirp of columns. If the device
 * configuration is changed it might be necessary to destroy (\ref ifx_rs_destroy) the old handle and
 * create a new one (\ref ifx_rs_create).
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     input     Real input matrix, with rows as chirps and columns as samples per chirp
 * @param [out]    output    Output is always a real vector of absolute magnitude spectrum of FFT size
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_run_r(ifx_RS_t* handle,
                  const ifx_Matrix_R_t* input,
                  ifx_Vector_R_t* output);

/**
 * @brief Performs signal processing on a real input I or Q (e.g. mean removal, windowing, zero padding,
 *        FFT transform) and produces a complex FFT spectrum as output.
 *        Here, second half of the spectrum is of no use as it is symmetric for real input FFT.
 *
 * The matrix input must have num_chirps_per_frame of rows and num_samples_per_chirp of columns. If the device
 * configuration is changed it might be necessary to destroy (\ref ifx_rs_destroy) the old handle and
 * create a new one (\ref ifx_rs_create).
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     input     Real input matrix, with rows as chirps and columns as samples per chirp
 * @param [out]    output    Output is complex FFT spectrum
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_run_rc(ifx_RS_t* handle,
                   const ifx_Matrix_R_t* input,
                   ifx_Vector_C_t* output);

/**
 * @brief Performs signal processing on a complex input IQ (e.g. mean removal, windowing, zero padding,
 *        FFT transform) and produces a complex FFT spectrum as output.
 *        Since the input is complex, thus output spectrum contains information over
 *        both positive and negative half of the spectrum.
 *
 * The matrix input must have num_chirps_per_frame of rows and num_samples_per_chirp of columns. If the device
 * configuration is changed it might be necessary to destroy (\ref ifx_rs_destroy) the old handle and
 * create a new one (\ref ifx_rs_create).
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     input     Complex input matrix, with rows as chirps and columns as samples per chirp
 * @param [out]    output    Output is complex FFT spectrum
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_run_c(ifx_RS_t* handle,
                  const ifx_Matrix_C_t* input,
                  ifx_Vector_C_t* output);

/**
 * @brief Performs signal processing on a complex input IQ (e.g. mean removal, windowing, zero padding,
 *        FFT transform) and produces a real amplitude spectrum of FFT size as output.
 *        Since the input is complex, thus output spectrum contains information over
 *        both positive and negative half of the spectrum.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     input     Complex input matrix, with rows as chirps and columns as samples per chirp
 * @param [out]    output    Output is always a real vector of absolute magnitude spectrum of FFT size
 *
 * The matrix input must have num_chirps_per_frame of rows and num_samples_per_chirp of columns. If the device
 * configuration is changed it might be necessary to destroy (\ref ifx_rs_destroy) the old handle and
 * create a new one (\ref ifx_rs_create).
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_run_cr(ifx_RS_t* handle,
                   const ifx_Matrix_C_t* input,
                   ifx_Vector_R_t* output);

/**
 * @brief Configures at runtime, the range spectrum mode in the handle. This helps
 *        not to create a new handle for new mode.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     mode      Update the range spectrum mode defined by \ref ifx_RS_Mode_t
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_set_mode(ifx_RS_t* handle,
                     ifx_RS_Mode_t mode);

/**
 * @brief Retrieves the current mode used within the range spectrum handle.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 *
 * @return Range spectrum mode defined by \ref ifx_RS_Mode_t
 *
 */
IFX_DLL_PUBLIC
ifx_RS_Mode_t ifx_rs_get_mode(const ifx_RS_t* handle);

/**
 * @brief Configures runtime index in single chirp mode index in the handle. Chirps index
 * starts from zero to positive number.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     index     Index is valid only for single chirp mode an non-negative number
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_set_single_chirp_mode_index(ifx_RS_t* handle,
                                        uint32_t index);

/**
 * @brief Retrieves the current single chirp mode index in the handle. Chirps index
 *        starts from zero to positive number.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 *
 * @return Index is valid only for single chirp mode an non-negative number
 *
 */
IFX_DLL_PUBLIC
uint32_t ifx_rs_get_single_chirp_mode_index(const ifx_RS_t* handle);

/**
 * @brief Configure at runtime, the range spectrum output to linear or dB scale in the handle.
 *
 * @param [in]     handle              A handle to the range spectrum processing object
 * @param [in]     scale_type          Linear or dB are the possible options.
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_set_output_scale_type(ifx_RS_t* handle,
                                  ifx_Math_Scale_Type_t scale_type);

/**
 * @brief Returns current range spectrum output scale i.e. linear or dB scale used within the handle.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 *
 * @return Linear or dB are the possible options.
 *
 */
IFX_DLL_PUBLIC
ifx_Math_Scale_Type_t ifx_rs_get_output_scale_type(const ifx_RS_t* handle);

/**
 * @brief Facilitates to update window parameters used before FFT operation.
 *        For example, if window type or its scale needs to be modified, one can update
 *        by passing the new window type or attenuation scale in window setting
 *        structure defined by \ref ifx_Window_Config_t.
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     config    Window configuration defined by \ref ifx_Window_Config_t
 *                           with new gain value or window type
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_set_window(ifx_RS_t* handle,
                       const ifx_Window_Config_t* config);

/**
 * @brief Copies the range spectrum matrix from range spectrum handle to the specified output container.
 *        Output matrix contains;
 *        1. Only single row containing FFT transform at the selected index in IFX_RS_MODE_SINGLE_CHIRP
 *        2. Fully populated matrix with FFT transforms in IFX_RS_MODE_COHERENT_INTEGRATION
 *        3. Only single row containing FFT transform at the Maximum Energy index in IFX_RS_MODE_MAX_ENERGY
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [out]    output    Pointer to Matrix of complex values containing the FFT transform (IQ)
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_copy_fft_matrix(const ifx_RS_t* handle,
                            ifx_Matrix_C_t* output);

/**
 * @brief Modifies the threshold value set within the Doppler spectrogram handle.
 *        Idea is to provide a runtime modification option to change threshold without destroy/create handle.
 *
 * @param [in]     handle    A handle to the range spectrum processing object.
 * @param [in]     threshold Threshold in linear scale. Range spectrum output values below this
 *                           are set to threshold value at the moment.
 */
IFX_DLL_PUBLIC
void ifx_rs_set_threshold(ifx_RS_t* handle, ifx_Float_t threshold);

/**
 * @brief Returns the currently used threshold within Range spectrum handle.
 *
 * @param [in]     handle    A handle to the range spectrum processing object.
 *
 * @return Current threshold value.
 *
 */
IFX_DLL_PUBLIC
ifx_Float_t ifx_rs_get_threshold(const ifx_RS_t* handle);

/**
 * @brief Range spectrogram is range spectrum over time
 *
 * @param [in]     handle    A handle to the range spectrum processing object
 * @param [in]     rx_idx    Rx antenna's index, value of '0' for first antenna, '1' for second antenna and so on.
 * @param [in]     static_target_removal  If true, then remove static targets from range spectrogram
 * @param [in]     input     Real valued range spectrum vector, which needs to be pushed to the history buffer
 * @param [out]    output    Output is always a real matrix of range spectrums over time
 *
 * The matrix out is build over time in terms of frame count e.g. for last 100 frames.
 *
 */
IFX_DLL_PUBLIC
void ifx_rs_spectrogram_r(ifx_RS_t* handle, uint32_t rx_idx, bool static_target_removal, const ifx_Vector_R_t* input, ifx_Matrix_R_t* output);


/**
 * @}
 */

/**
 * @}
 */

#ifdef __cplusplus
}  // extern "C"
#endif

#endif /* IFX_RADAR_RANGE_SPECTRUM_H */
