GPS-aware datetime module
=========================

This package provides GPS time conversion utilities, including a
gpstime subclass of the built-in datetime class with the addition of
GPS time parsing and conversion methods.

Leap second data, necessary for GPS time conversion, is expected to be
provided by the core libc Time Zone Database tzdata (on linux).  If
for some reason the tzdata leapsecond file is not available, a local
cache of the IERS leap second record will be maintained:

  https://hpiers.obspm.fr/iers/bul/bulc/ntp/leap-seconds.list

The package can be executed as a command-line GPS conversion utility.
In this manor it is a rough work-alike to the LIGO "tconvert" utility.
