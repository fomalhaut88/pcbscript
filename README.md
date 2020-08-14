# pcbscript

Pcbscript is a compiler to generate a PCB structure from a text file written according to an internal DSL ([domain sepcific language](https://en.wikipedia.org/wiki/Domain-specific_language)) that is described below. DSL contains variables, loops, macroses, if-else statements, translation block, etc. The mission of Pcbscript is to make the PCB design easier, using a programming language instead of a graphical software.

![Pcbscript](https://github.com/fomalhaut88/pcbscript/blob/master/examples/example.png?raw=true)


## Installation

As far as Pcbscript is written in Python, it can be installed as an ordinary Python library. For Windows/Linux/Mac:

```
python -m pip install git+https://github.com/fomalhaut88/pcbscript.git
```

**The version of python must be 3.5 or higher.**


## Usage

Show version:

    pcbscript version

Compile into a text file:

    pcbscript compile -i example.pcbs -o example.txt

Compile into an SVG image:

    pcbscript draw -i example.pcbs -o example.svg

Compile into an SVG image and redraw it every time when a change happens:

    pcbscript draw -i example.pcbs -o example.svg --watch

Prepare a picture on a sheet of paper to print (`offset` is in inches):

    pcbscript prepare -i example.pcbs -o example.jpg --dpi 300 --offset 1,1


## Snippets

### Basic items

    # Default options for drawing
    option GAP = 0.1
    option PIN_DIN = 0.25 
    option PIN_DOUT = 0.875
    option WIRE_WIDTH = 0.5
    option TEXT_HEIGHT = 0.75
    
    # Define board size
    board 15,7

    # Rounded pin
    pin 3,4  # In coordinates
    pin 3,5 1.25  # With external radius
    pin 3.6 1.25 1.0  # With external and internal radiuses

    # Square pin
    pinq 2,4
    pinq 2,5 1.25
    pinq 2,6 1.25 1.0

    # Wire
    wire 3,4 3,5  # Between two coordinates
    wire 3,6 1,6 2,5  # As polygonal chain
    wire 2,3 2,4 0.25  # With wire width

    # Text
    text "This is Pcbscript" 5,1  # In coordinates
    text "This is Pcbscript" 8,1 2.0  # With line height

    # Exit
    exit

### Variables

    var a = 5

    pin a,2
    pin (a + 1),3
    pin (2*a),(3*a)

### Loop

    for i in 0..5:
        pin i,1
        pin i,3

### if-else

    var a = 5

    if a > 2:
        pin 1,1
    else:
        pin 0,0

### Translate

    translate 10,4:
        pin 1,1  # Will be drawn in 11,5 because of the translation
        pin 1,2  # Will be drawn in 11,6 because of the translation

Translations can be embedded.

### Macro

    # Definition
    macro dipv(x, y, n):
        translate x,y:
            for i in 0..n:
                pin 0,i
                pin 4,i

    # Call
    dipv(4, 2, 4)

## A full example

    # Options

    option GAP = 0.1
    option PIN_DIN = 0.25
    option PIN_DOUT = 0.875
    option WIRE_WIDTH = 0.5
    option TEXT_HEIGHT = 0.75


    # Board

    board 15,7


    # Input and output pins

    pinq 1,1
    pinq 1,6
    pinq 14,1
    pinq 14,6


    # DIP

    macro dipv(x, y, n):
        translate x,y:
            for i in 0..n:
                pin 0,i
                pin 4,i

    dipv(4, 2, 4)


    # Wires

    wire 1,1 3,1 4,2
    wire 1,6 2,5 2,4 3,3 4,3
    wire 4,4 4,5
    wire 8,3 10,3
    wire 14,3 14,1
    wire 8,5 9,6 14,6
    wire 8,2 7,2 7,4 8,4


    # Pins

    pin 14,3
    pin 10,3


    # Text

    text "Example" 6,1


    # Rotation

    translate 6,5.5:
        rotate 45:
            pin -0.5,0
            pin 0.5,0
            wire -0.5,0 0.5,0
