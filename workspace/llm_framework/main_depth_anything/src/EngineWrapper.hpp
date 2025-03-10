/**************************************************************************************************
 *
 * Copyright (c) 2019-2023 Axera Semiconductor (Ningbo) Co., Ltd. All Rights Reserved.
 *
 * This source file is the property of Axera Semiconductor (Ningbo) Co., Ltd. and
 * may not be copied or distributed in any isomorphic form without the prior
 * written consent of Axera Semiconductor (Ningbo) Co., Ltd.
 *
 **************************************************************************************************/

#pragma once

#include <cstdint>
#include <opencv2/opencv.hpp>
#include "ax_engine_api.h"

#ifndef UNUSE_STRUCT_OBJECT
namespace detection {
typedef struct Object {
    cv::Rect_<float> rect;
    int label;
    float prob;
    cv::Point2f landmark[5];
    /* for yolov5-seg */
    cv::Mat mask;
    std::vector<float> mask_feat;
    std::vector<float> kps_feat;
    /* for yolov8-obb */
    float angle;
} Object;

}  // namespace detection
#endif

class EngineWrapper {
public:
    EngineWrapper() : m_hasInit(false), m_handle(nullptr)
    {
    }

    ~EngineWrapper()
    {
        Release();
    }

    int Init(const char* strModelPath, uint32_t nNpuType = 0);

    int SetInput(void* pInput, int index);

    int RunSync();

    int Post_Process(cv::Mat& mat, std::string& model_type, std::string& byteString);

    int GetOutput(void* pOutput, int index);

    int GetInputSize(int index);
    int GetOutputSize(int index);

    int Release();

protected:
    bool m_hasInit;
    AX_ENGINE_HANDLE m_handle;
    AX_ENGINE_IO_INFO_T* m_io_info{};
    AX_ENGINE_IO_T m_io{};
    int m_input_num{}, m_output_num{};
};
