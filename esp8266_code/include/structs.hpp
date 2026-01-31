#pragma once

struct FeedEvent {
    unsigned long timestamp; // Time of the feeding event
    unsigned int amount;     // Amount of food dispensed in grams
};
