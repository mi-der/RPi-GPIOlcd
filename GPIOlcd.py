#!/usr/bin/python

# -------------------------------------------- 
# GPIOlcd.py
# --------------------------------------------
#
# MIT License
#
# Copyright (c) 2020 Michael Schleider
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import RPi.GPIO as GPIO
import time

class lcd16x2:

    # Pre-Defined Commands
    _CLEAR = "00000001"
    _HOME = "00000010"
    _SETENTRY = "00000110"
    _SETFUNC = "00111000"

    # Enable pin timing
    _DELAY = 0.0001

    # Current Cursor Position
    _CURSORPOS = 0

    # ---
    #
    # _textToBinary(str)
    #
    # Description:
    #      Accepted a string to be converted to a list of binary strings
    #
    # Returns:
    #    [str]
    #
    # Parameters:
    #     - text: (str) String of ASCII characters.
    #
    # ---
    def _textToBinary(self, text):
        binary = []
        if all(ord(c) < 128 for c in text): # Check if all characters in the string are ASCII-compatable characters

            for c in text:

                byte = str(bin(ord(c))) # Convert curent character to binary
                byte = byte[2:] # Remove '0b' conversion prefix

                if len(byte) != 8: # If not 8 bits, make it 8 bits
                    p = 8 - len(byte)
                    byte = ("0"*p) + byte

                binary.append(byte) # Append to `binary` list

            return binary
        else:
            raise ValueError("Text to convert must only contain ASCII characters")



    # ---
    #
    # _sendBinary(str, bool)
    #
    # Description:
    #     Will send binary data through the assigned data pins.
    #
    # Parameters:
    #     - b: (str) Must have length of 8 and consist of characters "0" or "1"
    #     - isData: (bool) `False` if `b` is to be considered an instruction.
    #                      `True` if `b` is to be considered an ASCII character.
    #
    # ---
    def _sendBinary(self, b, isData):
        if type(b) == str: # Ensure `b` is of type str
            if len(b) == 8: # Ensure `b` is exactly 8 characters long
                if type(isData) == bool: # Ensure `isData` is of type bool

                    GPIO.output(self._RS, isData) # Set Register select pin
                    
                    GPIO.output(self._E, True) # Turn on Enable pin
                    time.sleep(self._DELAY)

                    # Set each of the data pins
                    for n in range(len(self._pins)):
                        GPIO.output(self._pins[7 - n], int(b[n]))
                        time.sleep(self._DELAY)

                    GPIO.output(self._E, False) # Turn off Enable pin
                    time.sleep(self._DELAY)

                else:
                    raise ValueError("Second parameter must be of type `bool`")
            else:
                raise ValueError("First parameter must have a string length equal to 8")
        else:
            raise ValueError("First parameter must be of type `str`")



    # ---
    #
    # _updateDisplay()
    #
    # Description:
    #     Will update the display's settings to user specification.
    #
    # ---
    def _updateDisplay(self):
        self._sendBinary("00001" + str(int(self._display)) + str(int(self._cursor)) + str(int(self._blink)), False)


    # ---
    #
    # clear()
    #
    # Description:
    #     Will clear the display and return the cursor home.
    #
    # ---
    def clear(self):
        self._CURSORPOS = 0
        self._sendBinary(self._CLEAR, False) # Clear the display
        self._sendBinary(self._SETFUNC, False) # Set the function of the display
        self._updateDisplay() # Set user settings
        self._sendBinary(self._SETENTRY, False) # Set the entry method of the display
        self._sendBinary(self._HOME, False) # Return to the home character

    # ---
    #
    # __init__(int, int, [int])
    #
    # Description:
    #     Initialize the lcd16x2 object.
    #
    # Parameters:
    #     - RS: (int) BCM Pin Number connected to the Register Select (RS) pin on the LCD Display
    #     - E: (int) BCM Pin Number connected to the Enable (E/EN) pin on the LCD Display
    #     - pins: ([int]) List of `int`, representing in order the BCM Pin Numbers connected to pins D0-D7 on the LCD Display
    #
    # ---
    def __init__(self, RS, E, pins):
        if type(RS) == int: # Ensure RS is of type `int`
            if type(E) == int: # Ensure E is of type `int`
                if type(pins) == list: # Ensure pins is of type `list`
                    if all(type(item) == int for item in pins): # Ensure each item in `list` pins is of type `int`
                        if len(pins) == 8: # Ensure `list` pins contains exactly 8 elements

                            # Store Instance Variables
                            self._RS = RS
                            self._E = E
                            self._pins = pins

                            # Store default settings
                            self._display = True # Should the display be on?
                            self._cursor = False # Should the cursor be enabled?
                            self._blink = False # Should the display show a blinking cursor?

                            # Set GPIO mode to BCM
                            GPIO.setmode(GPIO.BCM)
                            # Ignore GPIO warnings
                            GPIO.setwarnings(False)

                            # Setup GPIO Pins
                            for pin in (RS, E): # Register Select and Enable pins
                                GPIO.setup(pin, GPIO.OUT)
                                GPIO.output(pin, False)

                            for pin in pins: # D0 - D7 pins
                                GPIO.setup(pin, GPIO.OUT)
                                GPIO.output(pin, False)

                            self.clear()

                        else:
                            raise ValueError("Third parameter (`list` of `int`) must contain exactly 8 elements")
                    else:
                        raise ValueError("Third parameter (`list`) must only contain int")
                else:
                    raise ValueError("Third parameter must be of type `list`")
            else:
                raise ValueError("Second parameter must be of type `int`")
        else:
            raise ValueError("First parameter must be of type `int`")



    # ---
    #
    # __del__()
    #
    # Description:
    #     Called when the lcd16x2 object is deinitialized.  Will cleanup GPIO assignments.
    #
    # ---
    def __del__(self):
        GPIO.cleanup()



    # ---
    #
    # setText(str)
    #
    # Description:
    #     Will set the display's text to user-defined text
    #
    # Parameters:
    #     - text: (str) Text to be displayed on the LCD
    #
    # ---
    def setText(self, text):
        if type(text) == str:
            if len(text) <= 32:
                if len(text) <= 16: # If the text only takes up one line
                    self.clear()

                    for byte in self._textToBinary(text): # Send text to LCD
                        self._sendBinary(byte, True)
                        self._CURSORPOS += 1

                    if self._CURSORPOS == 15: # If it fills up the whole first line, might as well just fill up the null characters
                        for _ in range(24):
                            self._sendBinary("00000000", True)
                            self._CURSORPOS += 1

                else: # If the text will require two lines
                    self.clear()

                    for byte in self._textToBinary(text[:16]): # Send the first 16 characters
                        self._sendBinary(byte, True)
                        self._CURSORPOS += 1

                    for _ in range(24): # Send NULL to fill 17-40
                        self._sendBinary("00000000", True)
                        self._CURSORPOS += 1

                    for byte in self._textToBinary(text[16:]): # Send characters from 16 forward
                        self._sendBinary(byte, True)
                        self._CURSORPOS += 1
            else:
                raise ValueError("Paramter 1 must not have length greater than 32")
        else:
            raise ValueError("Paramter 1 must be of type str")



    # ---
    #
    # append(str)
    #
    # Description:
    #     Will set the display's text to user-defined text
    #
    # Parameters:
    #     - text: (str) Text to be appended to the current text on the LCD
    #
    # ---
    def append(self, text):
        if type(text) == str:
            if text != "":
                if (text != "") and (((self._CURSORPOS <= 16) and (self._CURSORPOS + 24 + len(text) <= 56)) or ((self._CURSORPOS >= 39) and (self._CURSORPOS + len(text) <= 56))): # Ensure the text does not excede the limits of the display
                    for byte in self._textToBinary(text):
                        if self._CURSORPOS == 16: # If the the first line is filled, send NULL to fill 17-40
                            for _ in range(24):
                                self._sendBinary("00000000", True)
                                self._CURSORPOS += 1

                        if self._CURSORPOS != 16: # Send the text
                            self._sendBinary(byte, True)
                            self._CURSORPOS += 1

                else:
                    raise ValueError("String is too long - total string must not excede 32 characters")
        else:
            raise ValueError("Paramter 1 must be of type str")



    # ---
    #
    # setDisplay(bool)
    #
    # Description:
    #     Will set the display either on or off
    #
    # Parameters:
    #     - value: (bool) `True` if display is to be turned on.
    #                     `False` if display is to be turned off.    
    #
    # ---
    def setDisplay(self, value):
        if type(value) == bool:
            self._display = value
            self._updateDisplay()
        else:
            raise ValueError("Paramter 1 must be of type bool")



    # ---
    #
    # setCursor(bool)
    #
    # Description:
    #     Will set the cursor either on or off
    #
    # Parameters:
    #     - value: (bool) `True` if cursor is to be turned on.
    #                     `False` if cursor is to be turned off.    
    #
    # ---
    def setCursor(self, value):
        if type(value) == bool:
            self._cursor = value
            self._updateDisplay()
        else:
            raise ValueError("Paramter 1 must be of type bool")



    # ---
    #
    # setBlink(bool)
    #
    # Description:
    #     Will set the blinking cursor either on or off
    #
    # Parameters:
    #     - value: (bool) `True` if blinking cursor is to be turned on.
    #                     `False` if blinking cursor is to be turned off.    
    #
    # ---
    def setBlink(self, value):
        if type(value) == bool:
            self._blink = value
            self._updateDisplay()
        else:
            raise ValueError("Paramter 1 must be of type bool")



    # ---
    #
    # displayOn()
    #
    # Description:
    #    Will turn on the LCD's display
    #
    # See Also:
    #    - setDisplay
    #
    # ---
    def displayOn(self):
        self.setDisplay(True)



    # ---
    #
    # displayOff()
    #
    # Description:
    #    Will turn off the LCD's display
    #
    # See Also:
    #    - setDisplay
    #
    # ---
    def displayOff(self):
        self.setDisplay(False)



    # ---
    #
    # cursorOn()
    #
    # Description:
    #    Will turn on the Cursor
    #
    # See Also:
    #    - setCursor
    #
    # ---
    def cursorOn(self):
        self.setCursor(True)
    


    # ---
    #  
    # cursorOff()
    #
    # Description:
    #    Will turn off the Cursor
    #
    # See Also:
    #    - setCursor
    #
    # ---
    def cursorOff(self):
        self.setCursor(False)



    # ---
    #
    # blinkOn()
    #
    # Description:
    #    Will turn on the blinking cursor
    #
    # See Also:
    #    - setBlink
    #
    # ---
    def blinkOn(self):
        self.setBlink(True)
    


    # ---
    #
    # blinkOff()
    #
    # Description:
    #    Will turn off the blinking cursor
    #
    # See Also:
    #    - setBlink
    #
    # ---
    def blinkOff(self):
        self.setBlink(False)