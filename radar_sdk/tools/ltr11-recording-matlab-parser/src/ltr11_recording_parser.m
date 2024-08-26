%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Copyright (c) 2022, Infineon Technologies AG
% All rights reserved.
%
% Redistribution and use in source and binary forms, with or without modification,are permitted provided that the
% following conditions are met:
%
% Redistributions of source code must retain the above copyright notice, this list of conditions and the following
% disclaimer.
%
% Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
% disclaimer in the documentation and/or other materials provided with the distribution.
%
% Neither the name of the copyright holders nor the names of its contributors may be used to endorse or promote
% products derived from this software without specific prior written permission.
%
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
% INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
% DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE  FOR ANY DIRECT, INDIRECT, INCIDENTAL,
% SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
% SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
% WHETHER IN CONTRACT, STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
% OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% DESCRIPTION:
% Parse data file to extract raw data for further processing
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [Frame, Header, Frame_count, fCkHz] = ltr11_recording_parser(sFile)
    fIDRaw = fopen([sFile '.raw.bin'], 'r', 'b'); % open file handle, big-endian style
    if( isequal(fIDRaw, -1) )
        error("file not found, or format not supported!\n");
    end
    
    Header.file_type_id = fread(fIDRaw, 4, 'char');
    if( ~isequal(char(Header.file_type_id'),'IFRB') )
        error("File type not supported!");
    end
    
    Header.file_format_version = fread(fIDRaw, 1, 'float');
    
    if(~check_config_BGT60LTR11(sFile,Header))
        warning("BGT60LTR11AIP configuration not found!");
    end
    
    Header = get_recordingheader(fIDRaw, Header);
    NumChirpData = Header.NumData;

    %% read in each frame
    n = 1;
    Frame = [];
    fread(fIDRaw, 1, 'uint8'); % peek into the next frame data block if there is any data available
    while(~feof(fIDRaw))
        fseek(fIDRaw, -1, 'cof');
        Frame = get_frameheader(fIDRaw, Header, Frame, n);
        
        if( length(Frame(n).RawData) == Header.NumData)
            % dispatch data
            Chirp = zeros(Header.Samples_per_Chirp, Header.Chirps_per_Frame, Header.Num_Rx_Antennas);
            % SamplesPerChirp = Header.Samples_per_Chirp;
            
            sn = 0:Header.Samples_per_Chirp-1; % zero based sample number
            
            if Header.Are_Rx_Antennas_Interleaved % interleaved antenna data
                switch Header.Data_Format_Enum
                    case 0 % EP_RADAR_BASE_RX_DATA_REAL: The frame data contains only I or Q signal
                        % data_value = pFrameStart[SAMPLE_NUMBER * num_rx_antennas + ANTENNA_NUMBER];
                        for nc = 0:Header.Chirps_per_Frame-1
                            for na = 0:Header.Num_Rx_Antennas-1
                                IData = Frame(n).RawData(1+ sn*Frame(n).Header.Num_Rx_Antennas + na + NumChirpData*nc); % real
                                % QData = []; % imag
                                Chirp(:,nc+1,na+1) = IData;
                            end
                        end
                        
                    case 1 % EP_RADAR_BASE_RX_DATA_COMPLEX: The frame data contains I and Q signals in separate data blocks
                        % data_value_real = frame_start[SAMPLE_NUMBER * num_rx_antennas + ANTENNA_NUMBER];
                        % data_value_imag = frame_start[(num_samples_per_chirp + SAMPLE_NUMBER) * num_rx_antennas + ANTENNA_NUMBER];
                        for nc = 0:Header.Chirps_per_Frame-1
                            for na = 0:Header.Num_Rx_Antennas-1
                                IData = Frame(n).RawData(1+ sn *Header.Num_Rx_Antennas + na + NumChirpData*nc); % real
                                QData = Frame(n).RawData(1+ (Header.Samples_per_Chirp + sn)*Header.Num_Rx_Antennas + na + NumChirpData*nc); % imag
                                Chirp(:,nc+1,na+1) = IData + 1i*QData;
                            end
                        end
                        
                    case 2 % EP_RADAR_BASE_RX_DATA_COMPLEX_INTERLEAVED: The frame data contains I and Q signals in one interleaved data block
                        % data_value_real = frame_start[2 * SAMPLE_NUMBER * num_rx_antennas + ANTENNA_NUMBER];
                        % data_value_imag = frame_start[2 * SAMPLE_NUMBER * num_rx_antennas + ANTENNA_NUMBER + 1];
                        for nc = 0:Header.Chirps_per_Frame-1
                            for na = 0:Header.Num_Rx_Antennas-1
                                IData = Frame(n).RawData(1+ 2*sn*Header.Num_Rx_Antennas + na     + NumChirpData*nc); % real
                                QData = Frame(n).RawData(1+ 2*sn*Header.Num_Rx_Antennas + na + 1 + NumChirpData*nc); % imag
                                Chirp(:,nc+1,na+1) = IData + 1i*QData;
                            end
                        end
                end
                
            else % non interleaved antenna data
                switch Header.Data_Format_Enum
                    case 0 % EP_RADAR_BASE_RX_DATA_REAL: The frame data contains only I or Q signal
                        % data_value = frame_start[ANTENNA_NUMBER * num_samples_per_chirp + SAMPLE_NUMBER];
                        for nc = 0:Header.Chirps_per_Frame-1
                            for na = 0:Header.Num_Rx_Antennas-1
                                IData = Frame(n).RawData(1+ na*Header.Samples_per_Chirp + sn + NumChirpData*nc); % real
                                % QData = []; % imag
                                Chirp(:,nc+1,na+1) = IData;
                            end
                        end
                        
                    case 1 % EP_RADAR_BASE_RX_DATA_COMPLEX: The frame data contains I and Q signals in separate data blocks
                        % data_value_real = frame_start[(2 * ANTENNA_NUMBER    ) * num_samples_per_chirp + SAMPLE_NUMBER];
                        % data_value_imag = frame_start[(2 * ANTENNA_NUMBER + 1) * num_samples_per_chirp + SAMPLE_NUMBER];
                        for nc = 0:Header.Chirps_per_Frame-1
                            for na = 0:Header.Num_Rx_Antennas-1
                                IData = Frame(n).RawData(1+  2*na   *Header.Samples_per_Chirp + sn + NumChirpData*nc); % real
                                QData = Frame(n).RawData(1+ (2*na+1)*Header.Samples_per_Chirp + sn + NumChirpData*nc); % imag
                                Chirp(:,nc+1,na+1) = IData + 1i*QData;
                            end
                        end
                        
                    case 2 % EP_RADAR_BASE_RX_DATA_COMPLEX_INTERLEAVED: The frame data contains I and Q signals in one interleaved data block
                        % data_value_real = frame_start[2 * ANTENNA_NUMBER * num_samples_per_chirp + 2*SAMPLE_NUMBER];
                        % data_value_imag = frame_start[2 * ANTENNA_NUMBER * num_samples_per_chirp + 2*SAMPLE_NUMBER + 1];
                        for nc = 0:Header.Chirps_per_Frame-1
                            for na = 0:Header.Num_Rx_Antennas-1
                                IData = Frame(n).RawData(1+ 2*na*Header.Samples_per_Chirp + 2*sn     + NumChirpData*nc); % real
                                QData = Frame(n).RawData(1+ 2*na*Header.Samples_per_Chirp + 2*sn + 1 + NumChirpData*nc); % imag
                                QData = -1*QData;  % on BGT60LTR11, sign of Q-signal needs to be inverted.
                                Chirp(:,nc+1,na+1) = IData + 1i*QData;
                            end
                        end
                end
            end
            
            Frame(n).Chirp = Chirp;
        else
            n = n - 1;
        end
        fread(fIDRaw, 1, 'uint8'); % peek into the next frame data block if there is any data available
        n = n+1;
    end
    Frame_count = n - 1;
    
    fCkHz = Header.Center_RF_Frequency_kHz;
    fclose(fIDRaw);
end

%% Check if recording is LTR11
function [result] = check_config_BGT60LTR11(sFile, Header)
    result = 1;
    if(Header.file_format_version == 1)
        sXML = xml2struct([sFile '.xml']); % parese xml file to struct
        if(~strcmp(sXML.Children(4).Name,'BGT60LTR11Endpoint'))
            result = 0;
            warning("Device not supported, missing 60LTR11 Endpoint in xml!");
        end
    elseif(any([3,4] == Header.file_format_version))
        fidjson = fopen([ sFile,'.json'],'rt');
        if(fidjson<0)
            result = 0;
            warning("Matching configuration file not found!");
        end
        jsondata = fread(fidjson);
        fclose(fidjson);
        json_config_info = jsondecode(char(jsondata'));
        if(~strcmp(json_config_info.device_info.device_name,'BGT60LTR11AIP'))
            result = 0;
            warning("Device not supported, BGT60LTR11AIP not found!");
        end
   else
       error("File type version not supported!");
   end
end

%% Populate Recording Header
function [Header] = get_recordingheader(fIDRaw, Header)
    if(Header.file_format_version == 1)
        Header.Header_Size = fread(fIDRaw, 1, 'int32');
        Header.Num_Tx_Antennas = fread(fIDRaw, 1, 'int32');
        Header.Num_Rx_Antennas = fread(fIDRaw, 1, 'int32');
        Header.Mask_Tx_Antennas = fread(fIDRaw, 1, 'int32');
        Header.Mask_Rx_Antennas = fread(fIDRaw, 1, 'int32');
        Header.Are_Rx_Antennas_Interleaved = fread(fIDRaw, 1, 'int32'); % If this is 0, the radar data of multiple RX antennas is stored in consecutive data blocks, where each block holds data of one antenna. If this is non-zero, the radar data of multiple RX antennas is stored in one data block, where for each point in time the samples from all RX antennas are stored consecutively before the data of the next point in time follows.
        Header.Modulation_Type_Enum = fread(fIDRaw, 1, 'int32');
        Header.Chirp_Shape_Enum = fread(fIDRaw, 1, 'int32');
        Header.Lower_RF_Frequency_kHz = fread(fIDRaw, 1, 'float');
        Header.Upper_RF_Frequency_kHz = fread(fIDRaw, 1, 'float');
        Header.Sampling_Frequency_kHz = fread(fIDRaw, 1, 'float');
        Header.ADC_Resolution_Bits = fread(fIDRaw, 1, 'int32'); % The ADC resolution of the data in sample_data.
        Header.Are_ADC_Samples_Normalized = fread(fIDRaw, 1, 'int32');
        Header.Data_Format_Enum = fread(fIDRaw, 1, 'int32'); % This indicates if the data is pDataBuffer is real or complex, and if complex data is interleaved. 0: real, 1: complex, 2: complex interleaved
        Header.Chirps_per_Frame = fread(fIDRaw, 1, 'int32'); % The number of chirps in this frame.
        Header.Samples_per_Chirp = fread(fIDRaw, 1, 'int32'); % The number of samples acquired in each chirp for each enabled RX antenna.
        Header.Samples_per_Frame = fread(fIDRaw, 1, 'int32'); % The number of samples acquired in each frame for each enabled RX antenna.
        Header.Chirp_Time_sec = fread(fIDRaw, 1, 'float');
        Header.Pulse_Repetition_Time_sec = fread(fIDRaw, 1, 'float');
        Header.Frame_period_sec = fread(fIDRaw, 1, 'float');
        %% for compatibility
        Header.Center_RF_Frequency_kHz = Header.Upper_RF_Frequency_kHz;
    elseif(any([3,4] == Header.file_format_version))
        Header.Header_Size = fread(fIDRaw, 1, 'int32');
        Header.Num_Tx_Antennas = fread(fIDRaw, 1, 'int32');
        Header.Num_Rx_Antennas = fread(fIDRaw, 1, 'int32');
        Header.Modulation_Type_Enum = fread(fIDRaw, 1, 'int32');
        Header.Center_RF_Frequency_kHz = fread(fIDRaw, 1, 'float');
        Header.Sampling_Frequency_kHz = fread(fIDRaw, 1, 'float');
        Header.ADC_Resolution_Bits = fread(fIDRaw, 1, 'int32'); % The ADC resolution of the data in sample_data.
        Header.Are_ADC_Samples_Normalized = fread(fIDRaw, 1, 'int32');
        Header.Data_Format_Enum = fread(fIDRaw, 1, 'int32'); % This indicates if the data is pDataBuffer is real or complex, and if complex data is interleaved. 0: real, 1: complex, 2: complex interleaved
        Header.Samples_per_Chirp = fread(fIDRaw, 1, 'int32'); % The number of samples acquired in each chirp for each enabled RX antenna.
        Header.Samples_per_Frame = fread(fIDRaw, 1, 'int32'); % The number of samples acquired in each frame for each enabled RX antenna.
        Header.Pulse_Repetition_Time_sec = fread(fIDRaw, 1, 'float');
        Header.Frame_period_sec = fread(fIDRaw, 1, 'float');
        %% params from legacy initialized with defaults
        Header.Chirps_per_Frame = 1;
        Header.Are_Rx_Antennas_Interleaved = 0;
    else
        error("File type version not supported!");
    end
    %## Data_Format_Enum_Def = {DATA_REAL = 0, DATA_COMPLEX = 1, DATA_COMPLEX_INTERLEAVED = 2}
    %## Chirp_Shape_Enum_Def = {UP_CHIRP = 0, DOWN_CHIRP = 1, UP_DOWN_CHIRP = 2, DOWN_UP_CHIRP = 3}
    %## Modulation_Type_Enum_Def = {DOPPLER = 0, FMCW = 1}
    
    switch (Header.Data_Format_Enum)
        case{0 1} % 0: real, 1: complex
            Header.SignalPart = 1; % Only one signal (I or Q) is captured during radar data frame acquisition.
        case(2) % 2: complex interleaved
            Header.SignalPart = 2; % Both, I and Q signal are captured as a complex signal during radar data frame acquisition.
    end
    NumChirpData = Header.Samples_per_Chirp * Header.Num_Rx_Antennas * Header.SignalPart; % Number of sample values per chirp
    Header.NumData = NumChirpData; % Number of sample values per frame
end

%% Populate Frame Header
function [Frame] = get_frameheader(fIDRaw, Header, Frame, n)
    if(Header.file_format_version == 1)
        Frame(n).Frame_Number = fread(fIDRaw, 1, 'int32'); % The running number of the data frame. The frame counter is, reset every time ep_radar_base_set_automatic_frame_trigger is called. If automatic frame trigger is not active, the frame counter may not work, and this could be 0.
        Frame(n).RawData = fread(fIDRaw, Header.NumData, '*single'); %#ok<*SAGROW> The buffer containing the radar data
    elseif(any([3,4] == Header.file_format_version))
        Frame(n).Frame_Number = fread(fIDRaw, 1, 'int32'); % The running number of the data frame. The frame counter is, reset every time ep_radar_base_set_automatic_frame_trigger is called. If automatic frame trigger is not active, the frame counter may not work, and this could be 0.
        Frame(n).Avg_Power = fread(fIDRaw, 1, 'float');
        Frame(n).Active = fread(fIDRaw, 1, 'int32');
        Frame(n).Motion = fread(fIDRaw, 1, 'int32');
        Frame(n).Direction = fread(fIDRaw, 1, 'int32');
        if(Header.file_format_version == 4)
            Frame(n).Amplitude = fread(fIDRaw, 1, 'int32');
            Frame(n).Timestamp = fread(fIDRaw, 1, 'int32');
        end
        Frame(n).RawData = fread(fIDRaw, Header.NumData, '*single'); %#ok<*SAGROW> The buffer containing the radar data
    else
        error("File type version not supported!");
    end
end
