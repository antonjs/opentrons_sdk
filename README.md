# OpenTrons Software Development Kit

[![Build Status](https://travis-ci.org/OpenTrons/opentrons_sdk.svg?branch=master)](https://travis-ci.org/OpenTrons/opentrons_sdk) [![Coverage Status](https://coveralls.io/repos/github/OpenTrons/opentrons_sdk/badge.svg?branch=master)](https://coveralls.io/github/OpenTrons/opentrons_sdk?branch=master)

The point of this repository is to provide a software equivalent to
an operating OpenTrons machine, including all related deck modules
and instruments (pipettes, tipracks, microplates, etc).

This current version has basic support for keeping track of liquids (and 
mixtures of liquids) between liquid containers.

It's currently exporting data concerning modules to a separate codebases
in charge of running the OpenTrons client.  An example of a minimalist Flask
client to calibrate and run a protocol can be found at 
[OpenTrons/sdk_demo](http://github.com/opentrons/sdk_demo).


## Protocols

Protocols are defined by importing the Protocol class, adding containers and
instruments, and finally defining commands.

Every instrument added must have a tiprack of the same size defined within
the protocol.

```python
from opentrons_sdk.protocol import Protocol

protocol = Protocol()

# Add containers.
protocol.add_container('A1', 'microplate.96')
protocol.add_container('C1', 'tiprack.p200')
protocol.add_container('B2', 'point.trash')

# Add a pipette (p200)
protocol.add_instrument('A', 'p200')

# Define transfers.
protocol.transfer('A1:A1', 'A1:A2', ul=100)
protocol.transfer('A1:A2', 'A1:A3', ul=80)
```

### Running on the Robot

To run a protocol on the OT-One machine, provide calibration data and then
attach the Protocol class to the serial port connected to the robot.

`Protocol.run` is a generator that will yield the current progress and total
number of commands within the protocol upon completion of each command.

To know when each command has been completed by the robot, it sends a special
debug command (`M62`) to the OpenTrons custom firmware and reads from the serial
device until the line `{"stat":0}` is found.

This functionaly can be changed by modifying 
[drivers.motor.OpenTrons](https://github.com/OpenTrons/opentrons_sdk/blob/master/opentrons_sdk/drivers/motor.py#L241).

```python
# Calibrate containers relative to the only instrument.
protocol.calibrate('A1', x=1, y=2, top=40, bottom=50)
protocol.calibrate('C1', x=100, y=100, top=40)
protocol.calibrate('B2', x=200, y=200, top=40)

# Attach to the robot via USB port.
protocol.attach_motor('/dev/tty.usbmodem1421')

# Run protocol.
for current, total in protocol.run():
    print("Completed command {} of {}.").format(current, total)

# Disconnect from the serial port.
protocol.disconnect()
```

### Context Awareness

The Protocol is capable of being context aware, in the sense that it
can use data about what's been attached to the protocol in order to
fill in variables automatically.

For example, if two pipettes are added to a protocol and a transfer is
specified without an explicitly defined axis or tool, the Context Handler
is capable of returning a pipette which supports that volume automatically.

### Protocol Handlers

The Protocol class itself is in charge of normalizing command arguments,
storing them, and passing that data to designated Handlers to perform the
work necessary to complete the protocol.

Two Handlers are defined by default, Context and MotorController.

#### Context Handler

The Context Handler is in charge of keeping track of the state of the robot,
calibrations, instruments, and other details using a virtualized deck map
with classes that correspond to each labware item.

Other Handlers may take advantage of this context in making intelligent
decisions regarding their operations.

#### Motor Handler

The Motor Handler takes high-level commands from the Protocol class and
translates them to serial data (G-Code) in order to perform these actions
on the robot itself.

If the Motor Handler is not attached to a USB port, it will still log
its movements and the serial commands it would have executed using the
standard `logging` library.

Additionally, the MotorHandler includes a PipetteMotor class which wraps
and tries to mimic the interface of a standard Pipette instance from the
labware portion of the codebase.

### Creating Additional Handlers

Additional handlers can be created by extending from ProtocolHandler. Once
you've created a new protocol handler, you can attach it using Protocol's
attach method.

The attach method takes a class and returns an instance, which can then be
manipulated at will.

### Protocol Data Format

From a design perspective, the main responsibility of the Protocol class is to
normalize arguments passed to command methods, such as transfer and distribute.

These calls are then stored within the class to be sent during the appropriate
times to any attached Protocol Handlers.

The data format is meant to be isomorphic with the OT-One JSON protocol, 
meaning that ingesting and exporting to our legacy format should be a simple
exercise.

## Compilers

This library has support for custom compilers, which will generate protocols
in JSON format to run on the original OT-One software.

## FusX

The only compiler currently in service is the one running on the backend of
[Mix.Bio's FusX](http://mix.bio/fusx) page.

This code can be called through the library by importing the pfusx module
from compilers.

Multiple sequences can be defined in either DNA or RVD format and compiled into
a single protocol output file.

```python
from opentrons_sdk.compilers import pfusx

inputs = [
	'NI NG NI HD HD NN NG HD NG NG NI NG NG NG NG',
	'ATACCRTCTTATTT'
]

pfusx.compile(*inputs)
```

## CSV Plate Maps

A utility for working with CSV Plate Maps is defined within the compiler
section of the framework.  Example plate map CSVs can be found in the 
[test fixtures](tests/fixtures), as well as the compiler 
[data directory](opentrons_sdk/compilers/data).

This allows third parties to specify well layouts within Excel and then
utilize that information for the creation of protocols.

Currently, this functionality is being used in the FusX compiler to replace
the original SQLite database from Mayo specifying plate positions, as well 
as in a test for Tipracks to ensure proper tip offset order.

## Command Engine

A command engine is provided to allow for the specification of high-level syntax
for human readable commands.

A decorator is provided to allow for setting complex syntaxes and then passing
parsed arguments from string-based input into the handler methods.

This functionality can be utilized within a Protocol Ingestor and perhaps a 
formatting system such as YAML to provide a new protocol language to replace
the JSON protocols.

### Argument Definition

Arguments are defined via regular expressions and given names as well
as human-readable examples of what the input should look like.

For example, the code below creates an argument syntax for a plate
definition.

```python
define_argument(
    'plate',
    '(([A-Z][1-9])|(\w+)):(([A-Z][1-9])|(\w+))',
    'A1:A1 or Plate1:A1'
)
```

### Command Definition

A function decorator is provided for the definition of full command
syntax.

The name of the method decorated becomes the name of the command.

The syntax string is composed of argument tags, which will be automatically
parsed by the execution handler (`execute`) and applied to the function.

An argument tag is a name of a defined argument within angular brackets
(< and >).  To define a label for an argument, place a colon after the
argument name and follow it with the desired argument name.

If no argument name is provided, then the argument will be passed as its
base argument name.

Documentation for the command handler can be provided to the user interface 
by utilizing Python's docstring access, available as `fn.__doc__`.

Additionally, metadata regarding argument definitions (as specified within
`define_argument`) may also be sent to the user interface.

```python
@syntax('<volume> from <plate:from_plate> to <plate:to_plate>')
def transfer(volume=None, from_plate=None, to_plate=None):
    """
    Transfers the specified amount of liquid from the start
    plate to the end plate.
    """
    # [...]
```

#### Full example

```python
from opentrons_sdk.engine.commands import define_argument, syntax, execute

define_argument(
    'plate',
    '(([A-Z][1-9])|(\w+)):(([A-Z][1-9])|(\w+))',
    'A1:A1 or Plate1:A1'
)

define_argument(
    'volume',
    '\d+[umµ]l',
    '10ul, 10ml, 10l, 10µl, etc.'
)

protocol = Protocol()

@syntax('<volume> from <plate:from_plate> to <plate:to_plate>')
def transfer(volume=None, from_plate=None, to_plate=None):
    """
    Transfers the specified amount of liquid from the start
    plate to the end plate.
    """
    protocol.transfer(volume, from_plate, to_plate)

execute("transfer 10µl from A1:A1 to A2:A2")

protocol.run()
```

## Labware

### Positions

Positions throughout this library are normalized into zero-indexed tuples
based on column letter and row number.  For example, "A1" becomes (0, 0).
Tuples may be passed to any system where a position argument is valid.

Full addresses of a deck slot and well within that slot are indicated
with a colon in string format (`"A1:A1"`) and as a list of tuples in 
normalized format (`[(0, 0), (0, 0)]`).

### Deck

All containers added to a Protocol are ultimately added to a deck, as part of
the "Virtual Robot" that runs the handler.

You can search for modules on the Deck by using `find_module` with keyword
arguments representing filters.

The filters work on dynamic properties as well, for example has_tips on
Tipracks.

```python
tiprack = deck.find_module(name="tiprack.p200", has_tips=True)
```

### Pipettes

Unlike containers, which are calibrated within the Context Handler, Pipettes store
their calibration values within the base labware class.  This is because Pipettes
will use their interal calibration values to make potentially complex calculations
based on volume.

Data collection and a more detailed `supports_volume` algorithm can account for 
working volumes.  It's possible to get increased accuracy from physical pipettes
by doing a distribution call using a larger volume instead of a single transfer
of a smaller volume.

Multi-channel pipettes are left as an exercise for the reader.  In the current 
implementation, multi-channel transfers are simply specified as single transfers
on the axis of a multi-channel pipette.

### Well Volumes

A complex liquid inventory system has been added to the labware containers.

Most of this functionality has been disabled for the time being, but could be
very useful to the creation of a more advanced protocol editor.

### Containers

The [labware.containers](opentrons_sdk/labware/containers.py) module provides data about
all supported containers, as well as conversions between old and new data
formats.

Containers can be specified by the user.

#### Listing Containers

```python
from opentrons_sdk.labware import containers

list = labware.containers.list_containers()
```

#### Defining a Container

Containers definitions are stored in [config/containers](opentrons_sdk/config/containers).
These are YAML files specifying the base type of container, the number of 
columns and rows, the A1 offset, and well margin.

See the documented [example container](opentrons_sdk/config/containers/example_plate.yml)
for more detailed instructions.

For containers with varying well or tube sizes, you can specify each
variation as a `custom_well` within the YAML structure.  See the
[15-50ml tuberack](opentrons_sdk/config/containers/tuberacks/15-50ml.yml) for an example of this
functionality being used.

#### Getting Container Well Offset

All container classes provide a static interface for getting non-calibrated
well offsets, which are all in reference to the A1 (or first coordinate) of
each plate.

```python
from opentrons_sdk.labware import containers

microplate = containers.load_container('microplate.24')
microplate.offset('A1')
```

#### Tipracks and Tip Inventory

Containers of the Tiprack type have the ability to return the position of a
tip from a given offset number of tips (which represent the tips that have
been used during the operation of the robot).

For example, the code below will provide the offset to the eleventh tip
position, in the event that the first ten have already been used.

A CSV containing a Plate Maps of tip offset order can be found in the
[test fixtures](tests/fixtures/offset_map.csv).  If the order is
changed, so should the offset map to ensure that the tests pass.

Tip offset can also be set at the Protocol level, and will allow the user
to specify how many tips have been used in a particular rack and automatically
switch to the next rack with remaining tips.

```python
from opentrons_sdk.labware import containers

tiprack = containers.load_container('tiprack.10ul')
tiprack.tip_offset(10)
```

#### User-Specific Containers

Users can provide their own YAML files specifying custom containers. These
containers can be stored anywhere, but must be loaded within the containers
module before being accessible.

This can be set to automatically load from a preloaded folder in the users'
documents for the desktop client.

```python
from opentrons_sdk.labware import containers

containers.load_custom_containers('/path/to/containers')
```

This will do a recursive glob through the directory provided and add all 
YAML files to the list of available labware containers.

#### Supported Container Types

As of this writing, supported container types are as follows:

* Grid (all containers extend from this base)
* Legacy (containers specified within the old containers.json format)
* Microplate
* Reservoir
* Tiprack
* Tuberack
* Point

For an up-to-date list, please use the `containers.list_container_types()`
method.

These types are implemented in the internal code and are currently not
extendable by the end user.
