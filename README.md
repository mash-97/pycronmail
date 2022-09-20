# pycronmail
`pycronmail` is an app that sends a basic system status mail to registered emails.

## Description
* This app consists of two programs `pycronmail` a bash file and `pyssmail.py` a
python file that collects system status and send it to the receiver email.

## `pycronmail`
* It is a basic CLI program for the app.
* It provides the basic interface for the user.
* It supports linux-debian environment.
* It has 3 commands: `install`, `set_config`, `add_receiver`.
* `install` to the CLI as a command parameter it installs the app in the current
user environment.
* `set_config` sets the sender email credentials.
* `add_receiver` add receiver email who will receive system status.

## `pyssmail.py`
* The purpose of the `pyssmail.py` program is to collect the system information, 
status and send it to the user through the use of email. 
* This program works if there is a python installed on the environment.

# Uses

After you have this repository on your disk, guide your terminal to this directory:
```bash
$ cd pycronmail
```

Install the app through the `pycronmail` bash script:
```bash
pycronmail$ chmod +x pycronmail
pycronmail$ ./pycronmail install 
pycronmail$ # or if you have python, python-psutil already installed
pycronmail$ ./pycronmail install --no-package-change 
```

After the successful installation there will have a job installed in the `crontab`.

To add receiver:
```bash
$ pycronmail add_receiver
```

To set sender credentials:
```bash
$ pycronmail set_config
```

# Conclusion
For the test purpose the `cronjob` will run the `pyssmail.py` program every minute!


