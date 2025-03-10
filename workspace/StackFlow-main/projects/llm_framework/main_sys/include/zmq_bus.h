/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#if __cplusplus
extern "C" {
#endif

void zmq_bus_work();
void zmq_bus_stop_work();

#if __cplusplus
}

#include "pzmq.hpp"
#include <vector>

using namespace StackFlows;

class unit_data {
private:
    std::unique_ptr<pzmq> user_inference_chennal_;

public:
    std::string work_id;
    std::string input_url;
    std::string output_url;
    std::string inference_url;
    int port_;

    unit_data();
    void init_zmq(const std::string &url);
    void send_msg(const std::string &json_str);
    ~unit_data();
};

int zmq_bus_publisher_push(const std::string &work_id, const std::string &json_str);
void zmq_com_send(int com_id, const std::string &out_str);

class zmq_bus_com {
private:
    int reace_event_;
    int raw_msg_len_;
    std::string raw_msg_buff_;

protected:
    std::string _zmq_url;
    int exit_flage;
    int err_count;
    int _port;
    std::string json_str_;
    int json_str_flage_;
    std::unique_ptr<std::thread> reace_data_event_thread;

public:
    std::unique_ptr<pzmq> user_chennal_;
    zmq_bus_com();
    void work(const std::string &zmq_url_format, int port);
    void stop();
    void select_json_str(const std::string &json_src, std::function<void(const std::string &)> out_fun);
    virtual void on_data(const std::string &data);
    virtual void on_raw_data(const std::string &data);
    virtual void send_data(const std::string &data);
    virtual void reace_data_event();
    virtual void send_data_event();
    ~zmq_bus_com();
};
#endif