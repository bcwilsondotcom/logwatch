logwatch
========

Python daemon which will monitor log files on your system looking for values. When seen, the message will be forwarded to a destination.

I created this script so that Chef cookbooks and/or Puppet modules could place a .conf file in /etc/logwatch.d/ and when the logwatch daemon starts, it will spawn a subprocess for each file in that directory and monitor for the events defined in the .conf file.

The .conf file format is as follows:
/patch/to/file.log,Message to Search For,Severity

Example:
/var/log/syslog,Operations Test,info

Using this setup, every piece of software that is placed on your system is responsible for informing the logwatcher daemon of what to look for. It decentralizes the log monitoring process and allows individuals responsible for the processes on the server, and usually on-call for that software, to easily define what they want to watch for.

The destination is defined in the syslog.handler near the top of the python script. I myself set the destination to our environment's Zenoss server which is running a zensyslog process. It recieves the message and creates visable and trackable events in the Zenoss GUI. It will also automatically page out for any events which we define with a severity of critical.
