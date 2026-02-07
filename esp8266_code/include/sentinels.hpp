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
* FILE: sentinels.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 1:47:36 07-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: These are pre-computed values to allow the program to know when it risks creating an overflow.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once

#include <cstdint>   // fixed-width integer types
#include <cstddef>   // size_t

/**
 * @file sentinel.hpp
 * @brief Compile-time sentinel values for embedded systems.
 *
 * This header provides constexpr sentinel values for common integer
 * types. It avoids <limits> and templates to reduce flash usage and
 * improve compile times on constrained targets such as ESP8266.
 *
 * All values are zero-cost and resolved entirely at compile time.
 */

 /* ───────────────────────── Signed integers ───────────────────────── */

constexpr int8_t   INT8_MIN_VALUE = INT8_MIN;
constexpr int8_t   INT8_MAX_VALUE = INT8_MAX;

constexpr int16_t  INT16_MIN_VALUE = INT16_MIN;
constexpr int16_t  INT16_MAX_VALUE = INT16_MAX;

constexpr int32_t  INT32_MIN_VALUE = INT32_MIN;
constexpr int32_t  INT32_MAX_VALUE = INT32_MAX;

/* ──────────────────────── Unsigned integers ───────────────────────── */

constexpr uint8_t  UINT8_MAX_VALUE = UINT8_MAX;
constexpr uint16_t UINT16_MAX_VALUE = UINT16_MAX;
constexpr uint32_t UINT32_MAX_VALUE = UINT32_MAX;

/* ───────────────────────── Platform-sized ─────────────────────────── */

constexpr size_t   SIZE_T_MAX_VALUE = SIZE_MAX;
