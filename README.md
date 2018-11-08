# Autexys Host

Automated Experimentation System Host and User Interface

## Setup and Dependencies

The python code is written in Python 3.

We recommend installing the [anaconda distribution](https://www.anaconda.com/download/) of python to satisfy many of the dependencies such as [numpy](http://www.numpy.org/), [matplotlib](https://matplotlib.org/), [flask](http://flask.pocoo.org/), etc.

Once the [anaconda distribution](https://www.anaconda.com/download/) of python 3 is installed, the following packages will also be needed:

- [pyVisa](https://pyvisa.readthedocs.io/en/master/)
- [pyVisa-py](https://pyvisa-py.readthedocs.io/en/latest/)
- [pySerial](https://pyserial.readthedocs.io/en/latest/shortintro.html)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)

These can typically be installed easily using a terminal by entering the following setup commands:

```console
pip install pyserial
pip install flask-socketio
pip install pyvisa
pip install pyvisa-py
```

In order to use the SMUs, a [backend](https://pyvisa.readthedocs.io/en/master/getting.html) needs to be installed for pyVisa.  PyVisa-py is one option for a backend, but it cannot collect data as quickly as the other backends, and it requires installation of dependencies such as libUSB. The typical route is to install a Visa Backend such as the one provided by NI. You can find more information about this in the [pyVisa documentation](https://pyvisa.readthedocs.io/en/master/getting_nivisa.html#getting-nivisa).

Especially for those less familiar with git, we recommend the [GitHub Desktop App](https://desktop.github.com/) be utilized to pull and push changes.

If desired, [Resilio Sync](https://www.resilio.com/individuals/) can be used to sync the data directory between your personal computers. The key for the data folder is: ALPORGP3DKHYE6STIG62DTRMGEANCCQ6O

