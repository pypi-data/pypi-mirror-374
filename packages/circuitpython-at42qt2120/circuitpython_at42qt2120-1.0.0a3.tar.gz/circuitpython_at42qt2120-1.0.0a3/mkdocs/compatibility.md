# MPR121 Compatible-use Audit

## Adafruit Examples

### [mpr121_simpletest.py](https://github.com/adafruit/Adafruit_CircuitPython_MPR121/blob/main/examples/mpr121_simpletest.py)

- Accesses channels via array subscripts.
- Accesses boolean from channels' values.

```py
#...
    if mpr121[i].value:
#...
```

### [mpr121_piano.py](https://github.com/adafruit/Adafruit_CircuitPython_MPR121/blob/main/examples/mpr121_piano.py)

- Accesses booleans from touched_pins tuple.

```py
#...
    touched = mpr121.touched_pins
#...
```

### [mpr121_pi_keyboard.py](https://github.com/adafruit/Adafruit_CircuitPython_MPR121/blob/main/examples/mpr121_pi_keyboard.py)

- Accesses channels via array subscripts.
- Accesses boolean from channels' values.

```py
#...
    if mpr121[pin].value:
#...
```

## Dependent Projects

### [CalThorndyke/GoldenOrchestra](https://github.com/CalThorndyke/GoldenOrchestra/)

- Accesses channels via array subscripts.
- Accesses boolean from channels' values.

```py
#...
    return mpr121[i].value
#...
```


### [directive0/picorderOS](https://github.com/directive0/picorderOS/)

- Accesses booleans from touched_pins tuple.

```py
#...
    touched = mpr121.touched_pins
#...
    for i in range(len(touched)):
#...
        if touched[i]:
#...
```


### [michaellee1019/mpr121](https://github.com/michaellee1019/mpr121/)

- Accesses channels via for...in.
- Accesses boolean from channels' values.

```py
#...
    return {"touchpads": [t.value for t in self.mpr121]}
#...
```


### [sabatesduran/rpi-touching-experience](https://github.com/sabatesduran/rpi-touching-experience/)

- Accesses channels via array subscripts.
- Accesses reading from channels' raw_values.
- Accesses boolean from channels' values.

```py
#...
    total_per_pin[i].append(mpr121[i].raw_value)
#...
    if average_per_pin and mpr121[i].value:
#...
```


### [mattange/menestrello](https://github.com/mattange/menestrello/)

- Accesses channels via array subscripts.
- Accesses boolean from channels' values.

```py
#...
    if self.mpr121[pin].value:
#...
        while self.mpr121[pin].value:
#...
```


### [Real-Human-Buisness/ast-2022](https://github.com/Real-Human-Buisness/ast-2022/)

- Accesses full (packed boolean) binary value via touched().
- Unpacks subset of bits manually.

```py
#...
    is_touched = cls.cap.touched()
#...
    cls.is_touched = tuple(bool(is_touched >> i & 1) for i in range(5))
#...
```

### Many Students of [IRL-CT/Developing-and-Designing-Interactive-Devices](https://github.com/IRL-CT/Developing-and-Designing-Interactive-Devices/)

- Access booleans from touched_pins tuple.
- Reset chip.
- Access channels via array subscripts.
- Access boolean from channels' values.

```py
#...
    touched = mpr121.touched_pins
#...
    while True not in touched:
#...
    mpr121.reset()
#...
    if mpr121[i].value:
#...
    if True in mpr121.touched_pins:
#...
    if mpr121[1].value or mpr121[0].value:
#...
```
