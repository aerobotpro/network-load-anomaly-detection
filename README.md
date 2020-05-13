# network-load-anomaly-detection
A basic machine learning system for detecting network recv/send anomalies/fluctuations on Linux machines (specifically servers).

# Requirements
- dstat
> dstat installation:
```sh
# RedHat/CentOS and Fedora
yum install dstat

# Debian, Ubuntu and Linux Mint
sudo apt-get install dstat
```
-------------------
- Python3.6+
> Install Requirements:

```sh
pip3 install -r requirements.txt
```
-----------------------
# Config
You can set your specific dataset name here
and also the interval amount per scan and the timing in between. 
Ensure that you use the same config on both your "training.py" and "detection.py"
files to avoid fatal inaccuracy.

```py
    #CONFIG
    INTERVAL_AMOUNT = 6
    INTERVAL_SECONDS = 1
    DATASET_NAME = "test1"
```
-----------------------
# Usage
To begin training, simply run `train.py`.
The longer you train, the better, and be sure to train during average traffic load.
If you train during an ongoing DDOS attack or during a peak visit time then your training data will reflect as such.

Two new directories will be created upon first instance, "datasets" and "sessions".

The "datasets" directory will represent your training data, as you'll see a sub-directory named for each of your datasets
that you have trained to.

The "sessions" directory represents your past sessions and their performance against our training data.

You may hardcode your own actions in "detection.py" in the lines marked as the following, here's a hardcoded example (psudocode):
```py
###
#<Increase/Decrease> <Amount>
###
os.system("A FIREWALL RULE IN RESPONSE TO RISE IN TRAFFIC")
###
```



