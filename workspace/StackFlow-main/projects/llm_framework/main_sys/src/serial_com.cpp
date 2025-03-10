/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include "serial.h"

#include <unistd.h>

#include <chrono>
#include <cstring>
#include <ctime>
#include <iostream>
#include <list>
#include <mutex>
#include <string>
#include <thread>
#include <vector>
#include <fstream>
#include <cstdio>

#include "all.h"
#include "event_loop.h"
#include "zmq_bus.h"
#include "linux_uart/linux_uart.h"
#include <memory>

class serial_com : public zmq_bus_com {
private:
    int uart_fd;

public:
    serial_com(uart_t *uart_parm, const std::string &dev_name) : zmq_bus_com()
    {
        uart_fd = linux_uart_init((char *)dev_name.c_str(), uart_parm);
        if (uart_fd <= 0) {
            SLOGE("open %s false!", dev_name.c_str());
            exit(-1);
        }
    }

    void send_data(const std::string &data)
    {
        if (exit_flage) linux_uart_write(uart_fd, data.length(), (void *)data.c_str());
    }

    void reace_data_event()
    {
        fd_set readfds;
        std::vector<char> buff(1024);
        while (exit_flage) {
            FD_ZERO(&readfds);
            FD_SET(uart_fd, &readfds);
            struct timeval timeout = {0, 500000};
            if ((select(uart_fd + 1, &readfds, NULL, NULL, &timeout) <= 0) || (!FD_ISSET(uart_fd, &readfds))) continue;
            ssize_t len = linux_uart_read(uart_fd, buff.size(), buff.data());
            if (len <= 0) continue;
            {
                try {
                    select_json_str(std::string(buff.data(), len),
                                    std::bind(&serial_com::on_data, this, std::placeholders::_1));
                } catch (...) {
                    std::string out_str;
                    out_str += "{\"request_id\": \"0\",\"work_id\": \"sys\",\"created\": ";
                    out_str += std::to_string(time(NULL));
                    out_str += ",\"error\":{\"code\":-1, \"message\":\"reace reset\"}}";
                    send_data(out_str);
                }
            }
        }
    }

    void stop()
    {
        zmq_bus_com::stop();
        linux_uart_deinit(uart_fd);
    }

    ~serial_com()
    {
        if (exit_flage) {
            stop();
        }
    }
};
std::unique_ptr<serial_com> serial_con_;

void serial_work()
{
    uart_t uart_parm;
    std::string dev_name;
    int port;
    memset(&uart_parm, 0, sizeof(uart_parm));
    SAFE_READING(uart_parm.baud, int, "config_serial_baud");
    SAFE_READING(uart_parm.data_bits, int, "config_serial_data_bits");
    SAFE_READING(uart_parm.stop_bits, int, "config_serial_stop_bits");
    SAFE_READING(uart_parm.parity, int, "config_serial_parity");
    SAFE_READING(dev_name, std::string, "config_serial_dev");
    SAFE_READING(port, int, "config_serial_zmq_port");

    serial_con_ = std::make_unique<serial_com>(&uart_parm, dev_name);
    serial_con_->work(zmq_s_format, port);

    if (access("/var/llm_update.lock", F_OK) == 0) {
        remove("/var/llm_update.lock");
        sync();
        std::string out_str;
        out_str += "{\"request_id\": \"0\",\"work_id\": \"sys\",\"created\": ";
        out_str += std::to_string(time(NULL));
        out_str += ",\"error\":{\"code\":0, \"message\":\"upgrade over\"}}";
        serial_con_->send_data(out_str);
    }
    if (access("/tmp/llm_reset.lock", F_OK) == 0) {
        remove("/tmp/llm_reset.lock");
        sync();
        std::string out_str;
        out_str += "{\"request_id\": \"0\",\"work_id\": \"sys\",\"created\": ";
        out_str += std::to_string(time(NULL));
        out_str += ",\"error\":{\"code\":0, \"message\":\"reset over\"}}";
        serial_con_->send_data(out_str);
    }
    sync();
}

void serial_stop_work()
{
    serial_con_.reset();
}
