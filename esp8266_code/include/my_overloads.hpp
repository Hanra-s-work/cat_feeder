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
* FILE: my_overloads.hpp
* CREATION DATE: 11-02-2026
* LAST Modified: 22:23:10 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: This is the file that tries to simplify string concatenations without relying of the heap heavy String command.
* // AR
* +==== END CatFeeder =================+
*/

#pragma once
#include <Print.h>
#include <string_view>
#include <type_traits>


// string_view support
inline Print &operator<<(Print &out, std::string_view sv)
{
    out.write(reinterpret_cast<const uint8_t *>(sv.data()), sv.size());
    return out;
}

// Arduino String support
inline Print &operator<<(Print &out, const String &s)
{
    out.write(reinterpret_cast<const uint8_t *>(s.c_str()), s.length());
    return out;
}

// C-string support
inline Print &operator<<(Print &out, const char *s)
{
    out.print(s);
    return out;
}

// single char
inline Print &operator<<(Print &out, char c)
{
    out.write(c);
    return out;
}

// Unsigned integers
template<typename T>
inline std::enable_if_t<std::is_unsigned_v<T>, Print &>
operator<<(Print &out, T value)
{
    out.print(value);
    return out;
}

// Signed integers
template<typename T>
inline std::enable_if_t<std::is_signed_v<T>, Print &>
operator<<(Print &out, T value)
{
    out.print(value);
    return out;
}

// custom std::endl
struct EndLine {};
inline constexpr EndLine endl{};
inline Print &operator<<(Print &out, EndLine)
{
    out.write('\n');   // or "\r\n" if you prefer
    return out;
}
