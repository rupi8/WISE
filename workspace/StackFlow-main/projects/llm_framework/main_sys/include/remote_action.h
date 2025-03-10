/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#if __cplusplus
extern "C" {
#endif
extern int unit_call_timeout;

int c_remote_call(const char *com_url, const char *server, const char *action, const char *obj);
#if __cplusplus
}
#include <string>
int remote_call(int com_id, const std::string &json_str);
void remote_action_work();
void remote_action_stop_work();
#endif