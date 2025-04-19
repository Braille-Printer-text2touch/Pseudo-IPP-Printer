# Pseudo IPP Printer

The IPP handling code for the Braille Printer. It creates and advirtises an IPP printer over mDNS. This "masquerades" as a networked printer with which users can interact while the code will send the print jobs over to the driver via a named pipe.

## How to Run

Once cloned and in the cloned directory

```bash
$ python3 -m venv .venv
.venv/bin/activate
pip3 install -r requirements.txt
sudo python3 ipp.py
```
