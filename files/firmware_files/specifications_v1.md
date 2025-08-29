# dashboard production specification

the dashboard producat has a small firmware 

## requirements for the firmware
1. The firmware on startup checks the time via NTP for that it uses a supplied function from a library named NTPtap NTP time check. If the NTP time check function returns a error code the foirmware shuts down the device

2. The dashboard displays values from different sources. The The values are provided by several functions named datasource1, datasource2, datasource3 the values are float.

3. The dashboard refreshes every minute.

4. The firmware is written in c.