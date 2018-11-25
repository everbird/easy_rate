# Easy-rate

**This is just a homework project for fun**

Easy-rate is a configurable command-line tool to make generating rate report easy. Basically it queries server statuses/calculates rate/generates report as you might expect, but all in a configurable manner.


The power of Easy-rate:

```
(easy-rate-1) ➜  easy_rate git:(master) ✗ curl http://localhost:8000/server-0001.status.json
{"Application": "Cache2", "Version": "1.0.1", "Uptime": 4637719417, "Request_Count": 5194800029, "Error_Count": 1042813251, "Success_Count": 4151986778}%
(easy-rate-1) ➜  easy_rate git:(master) ✗ curl http://localhost:8000/server-0002.status.json
{"Application": "Webapp1", "Version": "1.2.2", "Uptime": 1572762564, "Request_Count": 2171887540, "Error_Count": 1066265249, "Success_Count": 1105622291}%
(easy-rate-1) ➜  easy_rate git:(master) ✗ curl http://localhost:8000/server-0003.status.json
{"Application": "Database2", "Version": "1.1.2", "Uptime": 5292759176, "Request_Count": 4130319104, "Error_Count": 839310048, "Success_Count": 3291009056}%
...
(easy-rate-1) ➜  easy_rate git:(master) ✗ curl http://localhost:8000/server-0998.status.json
{"Application": "Cache1", "Version": "0.0.3", "Uptime": 2265003223, "Request_Count": 7311023147, "Error_Count": 4612143282, "Success_Count": 2698879865}%
(easy-rate-1) ➜  easy_rate git:(master) ✗ curl http://localhost:8000/server-0999.status.json
{"Application": "Webapp2", "Version": "0.0.1", "Uptime": 8743007122, "Request_Count": 7687687281, "Error_Count": 4160318641, "Success_Count": 3527368640}%
(easy-rate-1) ➜  easy_rate git:(master) ✗ curl http://localhost:8000/server-1000.status.json
{"Application": "Cache1", "Version": "1.1.2", "Uptime": 9281660375, "Request_Count": 4028121672, "Error_Count": 3240617982, "Success_Count": 787503690}%
(easy-rate-1) ➜  easy_rate git:(master) ✗ head -n 3 demo/servers.txt
server-0001
server-0002
server-0003
(easy-rate-1) ➜  easy_rate git:(master) ✗ cat demo/servers.txt | wc -l
    1000
(easy-rate-1) ➜  easy_rate git:(master) ✗ cat config/success_rate.conf
[QUERY]
concurrent = 3
status_url_template = http://localhost:8000/{server}.status.json

[RATE]
keys = app,version
denominator = total
nominator = success

[SCHEMA]
app = .Application
version = .Version
total = .Request_Count
success = .Success_Count
failure = .Error_Count

[REPORT]
rate_format = {:.2%%}
format = df

[ALIAS]
app = Application
version = Version
rate = Success Rate
(easy-rate-1) ➜  easy_rate git:(master) ✗ easy-rate -l demo/servers.txt -c config/success_rate.conf
    Application Version Success Rate
0        Cache0   0.0.1       59.36%
1        Cache0   0.0.2       54.74%
2        Cache0   0.0.3       59.33%
3        Cache0   0.1.0       64.76%
...
159     Webapp2   1.2.0       61.90%
160     Webapp2   1.2.1       55.99%
161     Webapp2   1.2.2       38.68%
(easy-rate-1) ➜  easy_rate git:(master) ✗ easy-rate -l demo/servers.txt -c config/success_rate.conf -f csv -o /tmp/success-rate-report.csv
(easy-rate-1) ➜  easy_rate git:(master) ✗ head -n 10 /tmp/success-rate-report.csv
Application,Version,Success Rate
Cache0,0.0.1,59.36%
Cache0,0.0.2,54.74%
Cache0,0.0.3,59.33%
Cache0,0.1.0,64.76%
Cache0,0.1.1,35.66%
Cache0,0.1.2,55.26%
Cache0,0.2.0,33.98%
Cache0,0.2.1,43.50%
Cache0,0.2.2,49.05%
(easy-rate-1) ➜  easy_rate git:(master) ✗ cat /tmp/success-rate-report.csv | wc -l
     163

```

Easy-rate allows you to config:
* Attributes for rate calculation
* Schema to take-in status response from server.
* Keys for aggregation
* Report display

Say that if you want Error Rate instead of Success Rate in above example, you can simply change to a new error_rate.conf as below:
```
(easy-rate-1) ➜  easy_rate git:(master) ✗ diff config/success_rate.conf config/error_rate.conf
8c8
< nominator = success
---
> nominator = failure
24c24
< rate = Success Rate
---
> rate = Error Rate
(easy-rate-1) ➜  easy_rate git:(master) ✗ easy-rate -l demo/servers.txt -c config/error_rate.conf
    Application Version Error Rate
0        Cache0   0.0.1     40.64%
1        Cache0   0.0.2     45.26%
2        Cache0   0.0.3     40.67%
3        Cache0   0.1.0     35.24%
...
159     Webapp2   1.2.0     38.10%
160     Webapp2   1.2.1     44.01%
161     Webapp2   1.2.2     61.32%

```

## Installation

```
python setup.py install
```

## Testing

```
python setup.py test
```

## Run it locally

You might don't have a list of server to provide status responses at hand. Fortunately you could run as simple http server to simulate that somehow.

Here are the steps to setup an environment in your local that easy-rate could run.

### STEP 0: Install pyenv
```
brew install pyenv
```

### STEP 1: Create your virtualenv
```
make NAME=easy-rate-2 prepare_virutalenv
```
It will install Python3.7.1, create a virtual environment named `easy-rate-2` and install dependencies from `requirments.txt` by default.
You can change them using parameter `NAME`, `PYVER` and `REQ`. Please read the Makefile for detail informaiton.

### STEP 2: Activate your virtualenv
```
pyenv activate easy-rate-2
```

### STEP 3: Run HTTP server
```
make nohup_runserver
```
It reads the demo/servers.txt and demo/responses.txt to produce json files in demo/stubs directory. Then it starts a simple HTTP server to serve these json files.

Make sure http://localhost:8000/ lists JSON files.

To Run eady-rate for these, you could use the config/success_rate.conf or you could create your own config. Remeber the `status_url_template` should match to your Simple HTTP Server.

```
# Install easy-rate first
python setup.py install

# Export the bin directory for easy-rate in your virtualenv
export PATH=$PATH:`pyenv virtualenv-prefix easy-rate-2`/envs/easy-rate-2/bin

# And run it!
easy-rate -l demo/servers.txt -c config/success_rate.conf
```
