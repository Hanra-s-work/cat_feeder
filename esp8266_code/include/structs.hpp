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
* FILE: structs.hpp
* CREATION DATE: 07-02-2026
* LAST Modified: 20:26:36 11-02-2026
* DESCRIPTION:
* This is the project in charge of making the connected cat feeder project work.
* /STOP
* COPYRIGHT: (c) Cat Feeder
* PURPOSE: These are structures used for tracking the feeding of the animal.
* // AR
* +==== END CatFeeder =================+
*/
#pragma once

struct FeedEvent {
    unsigned long timestamp; // Time of the feeding event
    unsigned int amount;     // Amount of food dispensed in grams
};
