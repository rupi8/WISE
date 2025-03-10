/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once
#include <pthread.h>
#include "sample_log.h"
#if __cplusplus

#include <map>
#include <string>
#include <any.hpp>
#include <unordered_map>

extern std::unordered_map<std::string, Any> key_sql;
extern pthread_spinlock_t key_sql_lock;

#define SAFE_READING(_val, _type, _key)               \
    do {                                              \
        pthread_spin_lock(&key_sql_lock);             \
        try {                                         \
            _val = any_cast<_type>(key_sql.at(_key)); \
        } catch (...) {                               \
        }                                             \
        pthread_spin_unlock(&key_sql_lock);           \
    } while (0)

#define SAFE_SETTING(_key, _val)            \
    do {                                    \
        pthread_spin_lock(&key_sql_lock);   \
        try {                               \
            key_sql[_key] = _val;           \
        } catch (...) {                     \
        }                                   \
        pthread_spin_unlock(&key_sql_lock); \
    } while (0)

#define SAFE_ERASE(_key)                    \
    do {                                    \
        pthread_spin_lock(&key_sql_lock);   \
        try {                               \
            key_sql.erase(_key);            \
        } catch (...) {                     \
        }                                   \
        pthread_spin_unlock(&key_sql_lock); \
    } while (0)

void load_default_config();

extern std::string zmq_s_format;
extern std::string zmq_c_format;

#endif

extern int main_exit_flage;

#if __cplusplus
extern "C" {
#endif

int ubus_alloc_work_id_num();

#if __cplusplus
}
#endif
