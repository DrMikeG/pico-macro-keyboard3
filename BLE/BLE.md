Blue tooth low energy.

I have a BLEFriend handy. I believe this is one with special firmware from Nordic on.

https://learn.adafruit.com/introducing-adafruit-ble-bluetooth-low-energy-friend/introduction


Please note that there are three versions of this board. 

An older v1.0 blue PCB which uses 16KB SRAM parts and can run firmware 0.5.0 and lower. 

A newer v2.0 black PCB that uses the latest 32KB parts and can run old firmware plus version 0.6.2 and higher, based on the FTDI bridge and with an SWD connector. 

A cost-optimized v3.0 board that uses a CP2104 USB chip and drops the SWD connector. v3.0 can run all of the same firmware as v2.0, and is the latest board available.

I have a version 3 board.

The v3.0 board uses the less expensive CP2104 USB to Serial bridge, which requires that you install the Silicon Labs VCP drivers on your system before using the board.

https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

Installed macOS_VCP_Driver and enabled in system settings.

Mode Selection Switch
This switch can be moved between 'CMD' (Command Mode) and 'UART' (Data Mode), which will change the way that the device behaves in your terminal emulator.

Command Mode
Command mode is used to send configuration commands to the module or retrieve information about the module itself or the device connected on the other side of the BLE connection.

To use command mode, make sure that the mode selection switch is set to CMD, and enter a valid Hayes AT style command using your favorite terminal emulator at 9600 bps (for example 'ATI' to display some basic info about the module).

If the MODE LED blinks three times followed by a three second delay you are in Command Mode:

```
---- Opened the serial port /dev/tty.SLAB_USBtoUART ----
---- Sent utf8 encoded message: "ATI\r\n" ----
ATI
BLEFRIEND32
nRF51822 0x00D6
C6FEEA6BA73C8F90
0.6.2
0.6.2
Apr 30 2015
S110 8.0.0, 0.2
OK
```

AT+HELP
+++,ATZ,ATI,ATE,AT+HELP,AT+FACTORYRESET,AT+DFU,AT+DBGMEMRD,AT+DBGNVMRD,AT+DBGSTACKSIZE,AT+DBGSTACKDUMP,AT+HWMODELED,AT+HWCONNLED,AT+HWRANDOM,AT+HWGETDIETEMP,AT+HWGPIOMODE,AT+HWGPIO,AT+HWI2CSCAN,AT+HWADC,AT+HWVBAT,AT+HWPWM,AT+HWPWRDN,AT+BLEPOWERLEVEL,AT+BLEGETADDRTYPE,AT+BLEGETADDR,AT+BLEBEACON,AT+BLEGETRSSI,AT+BLEURIBEACON,AT+GAPGETCONN,AT+GAPDISCONNECT,AT+GAPDEVNAME,AT+GAPDELBONDS,AT+GAPINTERVALS,AT+GAPSTARTADV,AT+GAPSTOPADV,AT+GAPAUTOADV,AT+GAPSETADVDATA,AT+BLEUARTTX,AT+BLEUARTRX,AT+BLEKEYBOARDCODE,AT+BLEKEYBOARDEN,AT+BLEKEYBOARD,AT+GATTADDSERVICE,AT+GATTADDCHAR,AT+GATTCHAR,AT+GATTLIST,AT+GATTCLEAR