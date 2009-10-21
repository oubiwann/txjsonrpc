#!/usr/bin/python
import os
import sys
from commands import getoutput
from subprocess import Popen
from time import sleep


examples = [
    ("tcp/client.py", "tcp/server.tac"),
    ("tcp/client_subhandled.py", "tcp/server_subhandled.tac"),
    ("web2/client.py", "web2/server.tac"),
    ]

expectedResults = [
    "Result: 8",
    """
    Result: [u'echo', u'math.add', u'system.listMethods', u'system.methodHelp', u'system.methodSignature', u'testing.getList']
    Result: [1, 2, 3, 4, u'a', u'b', u'c', u'd']
    Result: 8
    Result: bite me
    Shutting down reactor...
    """,
    "8",
    ]

def preprocess(result):
    return sorted([x.strip() for x in result.strip().split("\n")])

for example, expectedResult in zip(examples, expectedResults):
    expectedResult = preprocess(expectedResult)
    client, server = example
    print "Checking examples/%s against examples/%s ..." % (client, server)
    # start server
    command = "twistd -l /dev/null -noy %s" % os.path.join("examples", server)
    pid = Popen(command, shell=True).pid
    sleep(2)
    # run client
    command = "python %s" % os.path.join("examples", client)
    result = preprocess(getoutput(command))
    # kill server
    os.kill(pid, 15)
    # check results
    if result != expectedResult:
        print "ERROR: expected '%s' but got '%s'" % (result, expectedResult)
        sys.exit(1)
