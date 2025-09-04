#ifndef ETHIOPIC_CALENDAR_H
#define ETHIOPIC_CALENDAR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Date structure for both calendars
typedef struct {
    int32_t year;
    int32_t month;
    int32_t day;
} date_t;

// Julian Day Number epoch offsets
#define JD_EPOCH_OFFSET_AMETE_ALEM     -285019L
#define JD_EPOCH_OFFSET_AMETE_MIHRET   1723856L
#define JD_EPOCH_OFFSET_GREGORIAN      1721426L

// Calendar constants
#define ETHIOPIC_MONTHS_PER_YEAR       13
#define ETHIOPIC_DAYS_PER_MONTH        30
#define ETHIOPIC_DAYS_PER_4_YEARS      1461
#define GREGORIAN_DAYS_PER_400_YEARS   146097
#define GREGORIAN_DAYS_PER_100_YEARS   36524
#define GREGORIAN_DAYS_PER_4_YEARS     1461
#define GREGORIAN_DAYS_PER_2000_YEARS  730485

// Function declarations
bool is_gregorian_leap(int32_t year);
bool is_valid_gregorian_date(int32_t year, int32_t month, int32_t day);
bool is_valid_ethiopic_date(int32_t year, int32_t month, int32_t day);
int64_t gregorian_to_jdn(int32_t year, int32_t month, int32_t day);
int64_t ethiopic_to_jdn(int32_t year, int32_t month, int32_t day, int64_t era);
date_t jdn_to_gregorian(int64_t jdn);
date_t jdn_to_ethiopic(int64_t jdn, int64_t era);
date_t ethiopic_to_gregorian(int32_t year, int32_t month, int32_t day, int64_t era);
date_t gregorian_to_ethiopic(int32_t year, int32_t month, int32_t day);
int64_t guess_era(int64_t jdn);

#ifdef __cplusplus
}
#endif

#endif // ETHIOPIC_CALENDAR_H
