/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include "all.h"
#include "hv/TcpServer.h"
#include <unordered_map>
// #include <functional>

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

#include "all.h"
#include "event_loop.h"
#include "zmq_bus.h"
#include "json.hpp"

using namespace hv;

std::atomic<int> counter_port(8000);
TcpServer srv;

class tcp_com : public zmq_bus_com {
private:
public:
    std::weak_ptr<hv::SocketChannel> channel;
    std::mutex tcp_server_mutex;
    tcp_com() : zmq_bus_com()
    {
    }

    void send_data(const std::string& data)
    {
        // tcp_server_mutex.lock();
        // if (exit_flage)
        // {
        //     auto tcp_channel = channel.lock();
        //     if(tcp_channel)
        //     {
        //         tcp_channel->write(data);
        //     }
        // }
        // tcp_server_mutex.unlock();
        auto tcp_channel = channel.lock();
        if (tcp_channel) {
            tcp_channel->write(data);
        }
    }
};

void onConnection(const SocketChannelPtr& channel)
{
    if (channel->isConnected()) {
        auto p_com     = channel->newContextPtr<tcp_com>();
        p_com->channel = channel;
        p_com->work(zmq_s_format, counter_port.fetch_add(1));
        if (counter_port.load() > 65535) counter_port.store(8000);
    } else {
        auto p_com = channel->getContextPtr<tcp_com>();
        // p_com->tcp_server_mutex.lock();
        p_com->stop();
        // p_com->tcp_server_mutex.unlock();
        channel->deleteContextPtr();
    }
}

void onMessage(const SocketChannelPtr& channel, Buffer* buf)
{
    int len    = (int)buf->size();
    char* data = (char*)buf->data();
    auto p_com = channel->getContextPtr<tcp_com>();
    p_com->tcp_server_mutex.lock();
    try {
        p_com->select_json_str(std::string(data, len), std::bind(&tcp_com::on_data, p_com, std::placeholders::_1));
    } catch (...) {
        std::string out_str;
        out_str += "{\"request_id\": \"0\",\"work_id\": \"sys\",\"created\": ";
        out_str += std::to_string(time(NULL));
        out_str += ",\"error\":{\"code\":-1, \"message\":\"reace reset\"}}";
        channel->write(out_str);
    }
    p_com->tcp_server_mutex.unlock();
}

void tcp_work()
{
    int listenport = 0;
    SAFE_READING(listenport, int, "config_tcp_server");

    int listenfd = srv.createsocket(listenport);
    if (listenfd < 0) {
        exit(-1);
    }
    printf("server listen on port %d, listenfd=%d ...\n", listenport, listenfd);
    srv.onConnection = onConnection;
    srv.onMessage    = onMessage;
    srv.setThreadNum(2);
    srv.start();
}
void tcp_stop_work()
{
    srv.stop();
}
