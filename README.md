# Autexys Host

Automated Experimentation System Host and User Interface

## Installation

The python code is written in Python 3.

We recommend installing the [anaconda distribution](https://www.anaconda.com/download/) of python to satisfy many of the dependencies such as [numpy](http://www.numpy.org/), [matplotlib](https://matplotlib.org/), [flask](http://flask.pocoo.org/), etc.

Once the [anaconda distribution](https://www.anaconda.com/download/) of python 3 is installed, the following packages will also be needed:

- [pyVisa](https://pyvisa.readthedocs.io/en/master/)
- [pyVisa-py](https://pyvisa-py.readthedocs.io/en/latest/)
- [pySerial](https://pyserial.readthedocs.io/en/latest/shortintro.html)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)

These can typically be installed easily using a terminal by entering the following setup commands:

```console
conda install pip
pip install pyserial
pip install flask-socketio
pip install pyvisa
pip install pyvisa-py
pip install igor
pip install lmfit
```

If pip cannot install these packages, it is highly likely that you need to add some Anaconda directories to the PATH environmental variable of your system. Usually the directories that need to be added are the Anaconda install directory itself as well as the Anaconda/Scripts folder inside of the install directory. To use pip on the Windows command prompt, you also usually need to add Anaconda/Library/bin and Anaconda/Library/mingw-w64/bin 

In order to use the SMUs, a [backend](https://pyvisa.readthedocs.io/en/master/getting.html) needs to be installed for pyVisa.  PyVisa-py is one option for a backend, but it cannot collect data as quickly as the other backends, and it requires installation of dependencies such as libUSB. The typical route is to install a Visa Backend such as the one provided by NI. You can find more information about this in the [pyVisa documentation](https://pyvisa.readthedocs.io/en/master/getting_nivisa.html#getting-nivisa).

We strongly recommend the [GitHub Desktop App](https://desktop.github.com/) be utilized to pull and push changes to the GitHub repository.

If desired, [Resilio Sync](https://www.resilio.com/individuals/) can be used to sync the data directory between your personal computers. The key for the data folder is: ALPORGP3DKHYE6STIG62DTRMGEANCCQ6O


## Usage

The most common method to launch Autexys is to open a terminal and execute

```console
python manager.py
```

On some systems, such as the Raspberry Pi, this may need to be

```console
python3 manager.py
```

If the terminal is not pointed at the `source` directory that contains `managery.py`, you will either have to change directories using the `cd` command or enter the relative or absolute path to `manager.py`.

The manager starts two processes, the user interface (`ui.py`), and the dispatcher (`dispatcher.py`). The dispatcher is responsible for running experiments, which it does by dispatching lines of schedule files to be executed.  Schedule files are `.json` files that specify any settings that need to be altered from the defaults in order to specify the details of the experiment to run.  These lines in the schedule file are also referred to as jobs.

The dispatcher can be launched and given a schedule file without the use of the manager. This is done by running `dispatcher.py` and passing it the path of the desired schedule file as the first command line argument, such as

```console
python dispatcher.py ../../AutexysData/user/project/schedules/scheduleFile.json
```

To run a script in high priority (to avoid timing delays, especially important for real time procedures like SGM Control), on Windows run

```console
start /high /b python dispatcher.py ../../AutexysData/user/project/schedules/scheduleFile.json
```

The user interface can also be run standalone if desired.

```console
python ui.py
```
