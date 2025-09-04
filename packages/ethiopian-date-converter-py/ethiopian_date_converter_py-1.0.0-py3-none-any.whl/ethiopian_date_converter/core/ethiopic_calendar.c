#include "ethiopic_calendar.h"
#include <math.h>

/**
 * Proper modulo function that handles negative numbers correctly
 * C's % operator doesn't work the same as mathematical modulo for negative numbers
 */
static int64_t mod(int64_t a, int64_t b) {
    int64_t result = a % b;
    return result < 0 ? result + b : result;
}

/**
 * Integer floor division (equivalent to Math.floor(a/b) in JavaScript)
 */
static int64_t floor_div(int64_t a, int64_t b) {
    return (a - mod(a, b)) / b;
}

/**
 * Determines if a Gregorian year is a leap year
 * Rules: Divisible by 4, except century years unless divisible by 400
 */
bool is_gregorian_leap(int32_t year) {
    return (year % 4 == 0) && ((year % 100 != 0) || (year % 400 == 0));
}

/**
 * Validates a Gregorian date
 */
bool is_valid_gregorian_date(int32_t year, int32_t month, int32_t day) {
    if (month < 1 || month > 12) return false;
    if (day < 1) return false;
    
    static const int days_in_month[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    int max_day = days_in_month[month];
    if (month == 2 && is_gregorian_leap(year)) max_day = 29;
    
    return day <= max_day;
}

/**
 * Validates an Ethiopian date
 */
bool is_valid_ethiopic_date(int32_t year, int32_t month, int32_t day) {
    if (month < 1 || month > 13) return false;
    if (day < 1) return false;
    
    if (month <= 12) {
        return day <= 30;
    } else { // month 13 (Pagume)
        // Ethiopian leap year: year % 4 == 3
        int max_day = ((year % 4) == 3) ? 6 : 5;
        return day <= max_day;
    }
}

/**
 * Converts Ethiopian date to Julian Day Number
 * Formula: JDN = era + 365 + 365 * (year - 1) + floor(year / 4) + 30 * month + day - 31
 */
int64_t ethiopic_to_jdn(int32_t year, int32_t month, int32_t day, int64_t era) {
    return era + 365 + 365 * (year - 1) + floor_div(year, 4) + 30 * month + day - 31;
}

/**
 * Converts Julian Day Number to Ethiopian date
 * Uses 4-year cycle arithmetic (1461 days = 4 * 365 + 1)
 */
date_t jdn_to_ethiopic(int64_t jdn, int64_t era) {
    date_t result;
    
    int64_t r = mod(jdn - era, ETHIOPIC_DAYS_PER_4_YEARS);
    int64_t n = mod(r, 365) + 365 * floor_div(r, 1460);
    
    result.year = (int32_t)(4 * floor_div(jdn - era, ETHIOPIC_DAYS_PER_4_YEARS) + 
                           floor_div(r, 365) - floor_div(r, 1460));
    result.month = (int32_t)(floor_div(n, ETHIOPIC_DAYS_PER_MONTH) + 1);
    result.day = (int32_t)(mod(n, ETHIOPIC_DAYS_PER_MONTH) + 1);
    
    return result;
}

/**
 * Converts Gregorian date to Julian Day Number
 * Complex formula accounting for leap years and month variations
 */
int64_t gregorian_to_jdn(int32_t year, int32_t month, int32_t day) {
    int64_t s = floor_div(year, 4) - floor_div(year - 1, 4) - 
                floor_div(year, 100) + floor_div(year - 1, 100) + 
                floor_div(year, 400) - floor_div(year - 1, 400);
    int64_t t = floor_div(14 - month, 12);
    int64_t n = 31 * t * (month - 1) + 
                (1 - t) * (59 + s + 30 * (month - 3) + floor_div(3 * month - 7, 5)) + 
                day - 1;
    return JD_EPOCH_OFFSET_GREGORIAN + 
           365 * (year - 1) + 
           floor_div(year - 1, 4) - 
           floor_div(year - 1, 100) + 
           floor_div(year - 1, 400) + 
           n;
}

/**
 * Converts Julian Day Number to Gregorian date
 * Most complex function - handles all Gregorian leap year rules
 */
date_t jdn_to_gregorian(int64_t jdn) {
    date_t result;
    static const int32_t month_days[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    int32_t days_in_month[13];
    
    // Copy month_days to modifiable array
    for (int i = 0; i < 13; i++) {
        days_in_month[i] = month_days[i];
    }
    
    // Calculate cycle remainders
    int64_t offset_jdn = jdn - JD_EPOCH_OFFSET_GREGORIAN;
    int64_t r2000 = mod(offset_jdn, GREGORIAN_DAYS_PER_2000_YEARS);
    int64_t r400 = mod(offset_jdn, GREGORIAN_DAYS_PER_400_YEARS);
    int64_t r100 = mod(r400, GREGORIAN_DAYS_PER_100_YEARS);
    int64_t r4 = mod(r100, GREGORIAN_DAYS_PER_4_YEARS);
    
    // Calculate days and leap adjustments
    int64_t n = mod(r4, 365) + 365 * floor_div(r4, 1460);
    int64_t s = floor_div(r4, 1095);
    
    // Calculate year
    int64_t aprime = 400 * floor_div(offset_jdn, GREGORIAN_DAYS_PER_400_YEARS) + 
                     100 * floor_div(r400, GREGORIAN_DAYS_PER_100_YEARS) + 
                     4 * floor_div(r100, GREGORIAN_DAYS_PER_4_YEARS) + 
                     floor_div(r4, 365) - 
                     floor_div(r4, 1460) - 
                     floor_div(r2000, 730484);
    
    result.year = (int32_t)(aprime + 1);
    
    // Calculate month and day
    int64_t t = floor_div(364 + s - n, 306);
    result.month = (int32_t)(t * (floor_div(n, 31) + 1) + 
                            (1 - t) * (floor_div(5 * (n - s) + 13, 153) + 1));
    
    n += 1 - floor_div(r2000, 730484);
    result.day = (int32_t)n;
    
    // Handle special century boundary case
    if ((r100 == 0) && (n == 0) && (r400 != 0)) {
        result.month = 12;
        result.day = 31;
    } else {
        // Adjust for leap year
        days_in_month[2] = is_gregorian_leap(result.year) ? 29 : 28;
        
        // Find correct month and day
        for (int i = 1; i <= 12; i++) {
            if (n <= days_in_month[i]) {
                result.day = (int32_t)n;
                break;
            }
            n -= days_in_month[i];
        }
    }
    
    return result;
}

/**
 * Automatically determines the correct era based on JDN
 * Returns AM for dates >= 5500 EC, AA for earlier dates
 */
int64_t guess_era(int64_t jdn) {
    return (jdn >= (JD_EPOCH_OFFSET_AMETE_MIHRET + 365)) ? 
           JD_EPOCH_OFFSET_AMETE_MIHRET : 
           JD_EPOCH_OFFSET_AMETE_ALEM;
}

/**
 * High-level Ethiopian to Gregorian conversion
 */
date_t ethiopic_to_gregorian(int32_t year, int32_t month, int32_t day, int64_t era) {
    int64_t jdn = ethiopic_to_jdn(year, month, day, era);
    return jdn_to_gregorian(jdn);
}

/**
 * High-level Gregorian to Ethiopian conversion with automatic era detection
 */
date_t gregorian_to_ethiopic(int32_t year, int32_t month, int32_t day) {
    int64_t jdn = gregorian_to_jdn(year, month, day);
    int64_t era = guess_era(jdn);
    return jdn_to_ethiopic(jdn, era);
}
