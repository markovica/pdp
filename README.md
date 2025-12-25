# pdp
Packet Drop Application Protool

# Description
Cold War 2.0 survival protocol
Uses packet drop pattern to hide data from interception.

# Usage

## Receiver
Start the receiver
```
python3 pdp.py receiver <expected byte count>
```
example
```
python3 pdp.py receiver 12
```

## Sender
Send the data
```
python3 pdp.py sender 127.0.0.1 "HELLO WORLD!"
```
example
```
python3 pdp.py sender 127.0.0.1 "HELLO WORLD!"
```
