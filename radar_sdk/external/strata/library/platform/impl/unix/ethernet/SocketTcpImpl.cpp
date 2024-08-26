/**
 * @copyright 2018 Infineon Technologies
 *
 * THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
 * KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
 * PARTICULAR PURPOSE.
 */

#include "SocketTcpImpl.hpp"

#include <common/Logger.hpp>
#include <platform/exception/EConnection.hpp>


ISocket::Mode SocketTcpImpl::getMode() const
{
    return ISocket::Mode::Stream;
}

void SocketTcpImpl::open(uint16_t localPort, uint16_t remotePort, ipAddress_t remoteIpAddr, uint16_t timeout)
{
    if (remoteIpAddr == nullptr)
    {
        throw EConnection("SocketTcpImpl::open - no remote ip address provided");
    }
    SocketImpl::open(localPort, remotePort, remoteIpAddr, timeout);
}

SocketImpl::SocketType SocketTcpImpl::socket()
{
    LOG(DEBUG) << "Opening SocketTcpImpl ...";

    return ::socket(AF_INET, SOCK_STREAM, 0);
}
