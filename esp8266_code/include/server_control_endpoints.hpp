/*
* +==== BEGIN CatFeeder =================+
* LOGO:
* ..............(....⁄\
* ...............)..(.')
* ..............(../..)
* ...............\(__)|
* Inspired by Joan Stark
* source https://www.asciiart.eu/
* animals/cats
* /STOP
* PROJECT: CatFeeder
* FILE: server_control_endpoints.hpp
* CREATION DATE: 14-02-2026
* LAST Modified: 12:22:21 14-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the file that will contain the endpoints used by the device to communicate with the central server.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once
#include <string_view>
#include "server.hpp"

namespace HttpServer
{
    namespace ServerEndpoints
    {
        namespace Url
        {

            namespace Get
            {
                inline constexpr std::string_view FED = "/api/v1/feeder/fed";
            } // namespace Get

            namespace Post
            {
                inline constexpr std::string_view FED = "/api/v1/feeder/fed";
                inline constexpr std::string_view LOCATION = "/api/v1/feeder/beacon/location";
                inline constexpr std::string_view VISITS = "/api/v1/feeder/visit";
            } // namespace Post

            namespace Put
            {
                inline constexpr std::string_view IP = "/api/v1/feeder/ip";
            } // namespace Put

            namespace Patch
            {
                // There is nothing to patch for the moment
            } // namespace Patch

            namespace Delete
            {
                // There is nothing to delete for the moment
            } // namespace Delete
        } // namespace Url
        namespace Handler
        {

            namespace Get
            {
                /* Check if the beacon near us need feeding (or is allowed to be fed)
                * Body:
                *   {
                *       "beacon_mac": {{sample_beacon}},
                *   }
                */
                bool fed(const char *beacon_mac, long long int *can_distribute);
            } // namespace Get

            namespace Post
            {
                /* Inform the parent server that we are feeding the beacon
                * Body:
                *   {
                *       "beacon_mac": {{sample_beacon}},
                *       "feeder_mac": {{sample_feeder}},
                *       "amount": {{feeder_amount}}
                *   }
                */
                bool fed(const char *beacon_mac, const unsigned long food_amount);

                /*inform the control server that the pet (beacon) has passed near us
                * Body:
                *   {
                *       "beacon_mac": {{sample_beacon}},
                *       "feeder_mac": {{sample_feeder}}
                *   }
                */
                bool location(const char *beacon_mac);
                /*inform the control server that the pet (beacon) has passed near us (fallback endpoint)
                * Body:
                *   {
                *       "beacon_mac": {{sample_beacon}},
                *       "feeder_mac": {{sample_feeder}}
                *   }
                */
                bool visits(const char *beacon_mac);
            } // namespace Post

            namespace Put
            {
                /*Update the feeder ip towards the main server
                * Body:
                * {
                *     "mac": {{sample_feeder}},
                *     "ip":{{feeder_ip}}
                * }
                */
                bool ip();
            } // namespace Put

            namespace Patch
            {
                // There is nothing to patch for the moment
            } // namespace Patch

            namespace Delete
            {
                // There is nothing to delete for the moment
            } // namespace Delete
        } // namespace Handler
    } // namespace ServerEndpoints
} // namespace HttpServer
