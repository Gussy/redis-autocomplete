#!/usr/bin/env python

import redis
import time
import sys

r = redis.Redis(host='localhost', port=6379, db=0)

filename = "female-names.txt"

if len(sys.argv) == 2 and sys.argv[1] == "--flush":
    print "Flushing Database"
    r.flushdb()

if not r.exists("compl"):
    t0 = time.time()
    print "Loading entries in the Redis DB"

    names = open(filename, "r")

    # Loop through each line
    for line in names:

        # Skip comments in the input file
        if line[0] == "#":
            continue

        # Loop for number of chars in line
        for i in range(len(line.strip())):
            if i == 0:
                continue
            
            # Add the prefix
            r.zadd("compl", **{line[:i]: 0})
            #print line[:i]

        # Print out full line
        out = "%s*" % line.strip()
        r.zadd("compl", **{out: 0})
        #print out
    names.close()
    print "Loaded in ", time.time() - t0, " seconds"
else:
    print "NOT loading entries, there is already a 'compl' key"

def complete(r, prefix, count):
    t0 = time.time()
    results = []
    rangelen = 50 # This is not random, try to get replies < MTU size
    start = r.zrank("compl", prefix)
    if start == None:
        return []
    while len(results) != count:
        zrange = r.zrange("compl", start, start+rangelen-1)
        start += rangelen
        if not zrange or len(zrange) == 0:
            break
        for entry in zrange:
            minlen = min(len(entry),len(prefix))
            if entry[0:minlen] != prefix[0:minlen]:
                count = len(results)
                break
            if entry[-1:] == "*" and len(results) != count:
                results.append(entry[:-1])
    print "Found %i entries in %.4f seconds" % (len(results), time.time() - t0)
    return results

print complete(r, "ma", 50)
print complete(r, "zu", 50)
