/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#if __cplusplus
extern "C" {
#endif

char const* c_sys_sql_select(char const* key);
void c_sys_sql_set(char const* key, char const* val);
void c_sys_sql_unset(char const* key);
void c_sys_allocate_unit(char const* unit, char* input_url, char* output_url, int* work_id);
int c_sys_release_unit(char const* unit);

#if __cplusplus
}
void remote_server_work();
void remote_server_stop_work();
#endif