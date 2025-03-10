/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include "all.h"
#include <string>
#include "remote_action.h"
#include "pzmq.hpp"
#include "json.hpp"
#include "StackFlowUtil.h"

using namespace StackFlows;

int unit_call_timeout;

int remote_call(int com_id, const std::string &json_str)
{
    std::string work_id   = sample_json_str_get(json_str, "work_id");
    std::string work_unit = work_id.substr(0, work_id.find("."));
    std::string action    = sample_json_str_get(json_str, "action");
    char com_url[256];
    int length = snprintf(com_url, 255, zmq_c_format.c_str(), com_id);
    std::string send_data;
    std::string com_urls(com_url);
    RPC_PUSH_PARAM(send_data, com_urls, json_str);
    pzmq clent(work_unit);
    return clent.call_rpc_action(action, send_data, [](pzmq *_pzmq, const std::string &val) {});
}

void remote_action_work()
{
    SAFE_READING(unit_call_timeout, int, "config_unit_call_timeout");
}

void remote_action_stop_work()
{
}
