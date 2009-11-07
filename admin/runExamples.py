#!/usr/bin/python
import os
import sys
from subprocess import Popen, PIPE
from time import sleep


examples = [
    ("tcp/client.py", "tcp/server.tac"),
    ("tcp/client_subhandled.py", "tcp/server_subhandled.tac"),
    ("web/client.py", "web/server.tac"),
    ("web2/client.py", "web2/server.tac"),
    ("webAuth/client.py", "webAuth/server.tac"),
    ("web2Auth/client.py", "web2Auth/server.tac"),
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
    """
    Result: 8
    Result: bite me
    Shutting down reactor...
    """,
    "Result: 8",
    """
    Unauthorized
    Unauthorized
    Result: 8
    Result: bite me
    Shutting down reactor...
    """,
    """
    Unauthorized
    Unauthorized
    Result: 8
    Result: bite me
    Shutting down reactor...
    """
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
    sleep(0.5)
    # run client
    command = "python %s" % os.path.join("examples", client)
    process = Popen(command, shell=True, stdout=PIPE)
    result = preprocess(process.communicate()[0])
    # kill server
    os.kill(pid, 15)
    # check results
    if result != expectedResult:
        print "ERROR: expected '%s' but got '%s'" % (expectedResult, result)
        sys.exit(1)
