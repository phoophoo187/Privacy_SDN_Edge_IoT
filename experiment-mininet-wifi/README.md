# Mininet-WiFi installation (08/2021)
In this project, we install Mininet-WiFi on Ubuntu18.04.
The official mininet-wifi site recommends using Ubuntu16.04 or higher.
We have tested installing on Ubuntu16.04 and Ubuntu20.04 and we got some errors.
For ubuntu16.04, it is preinstalled with python3.5 which is an obsolete version. 
We don't want to install python3.6 or higher by ourselves and we need the new version of libs and other software. 
So we move to the newer version of Ubuntu which is 20.04.
For ubuntu20.04, we got some errors about strncopy in python. It might be because the libs are too new for mininet-wifi.
That is why we decided to use Ubuntu18.04.
<br>
## Installation
After we got a clean installation and updated of Ubuntu18.04. 
We follow these steps.
- **step 1:** $sudo apt-get update
- **step 2:** $sudo apt-get upgrade
- **step 3:** $sudo apt-get install build-essential
- **step 4:** $sudo apt-get install autoconf automake gdb git
- **step 5:** $sudo apt-get install python3.6-dev
- **step 6:** $sudo apt-get install python3-pip
- **step 7:** $python3 -m pip --version    #check pip version
- **step 8:** $pip3 install --upgrade pip  #upgrade pip to the current version

### Step 9 to 12 install mininet-wifi 
The mininet-wifi page is https://github.com/intrig-unicamp/mininet-wifi. <br>
We recommend creating a parent folder to store the mininet-wifi source code before running the git clone command.
- **step 9:** $git clone https://github.com/intrig-unicamp/mininet-wifi
- **step 10:** $cd mininet-wifi
- **step 11:** $sudo util/install.sh -Wlnfv
<br>*install.sh options:
<br>-W: wireless dependencies
<br>-n: mininet-wifi dependencies
<br>-f: OpenFlow
<br>-v: OpenvSwitch
<br>-l: wmediumd*
- **step 12:** $sudo util/install.sh -3f 
<br>*install.sh options:
<br>-3: installs OpenFlow 1.3 versions
<br>-f: OpenFlow*
<br>Note: we have tried to combine step 11 and 12 with -Wln3fv option but we got some errors 

<br>In this work, we need The Ryu controller https://ryu.readthedocs.io/en/latest/getting_started.html.
<br> We have tested installing the Ryu from pip directly. We got error about eveltlet.wsgi which is 'cannot import name ALREADY_HANDLED'. So, we install Ryu from the source code instead.
- **step 13:** $sudo apt-get install gcc python3-dev libffi-dev libssl-dev libxm12-dev libxslt1-dev zlib1g-dev
<br> At step 13 we follow the instruction on the https://ryu.readthedocs.io/en/latest/getting_started.html.
- **step 14:** $git cl% git clone https://github.com/faucetsdn/ryu.git
- **step 15:** $cd ryu
- **step 16:** $pip3 install
- **step 17:** $pip install -r tools/optional-requires   #install extra packages
<br>#Note make sure pip3 is not too old in order to avoid any installation error.

## Runing an Experiment
To setup the topology for the experiment
- $sudo python3 topology.py
<br> After mininet-wifi is run and all nodes are loaded, we will get the *mininet-wifi>* prompt. 
Run the command below to oper terminal in the h1.

![image](https://user-images.githubusercontent.com/13536277/128671129-d8ef97fa-a7b9-43fd-b8bf-9556459fb992.png)

- **mininet-wifi>** xterm h1 
<br> the new xterm window of **node:h1** is opened. At the prompt run ryuAtSuperEdge.py
- #python3 ryuAtSuperEdge.py


(<-- two spaces)
Interesting link

https://www.grotto-networking.com/SDNfun.html
