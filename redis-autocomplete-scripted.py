#!/usr/bin/env python

import redis
import time
import sys

r = redis.Redis(host="localhost", port=6379, db=0)

filename = "female-names.txt"

adderscript = \
"""
for i=1,(#ARGV[1]-1) do
  prefix = string.sub(ARGV[1], 0, i)
  redis.call('zadd', KEYS[1], 0, prefix)
end
redis.call('zadd', KEYS[1], 0, string.format("%s*", ARGV[1]))
"""

completescript = \
"""
local count = tonumber(ARGV[2])
local results = {}
local rangelen = 50
local start = tonumber(redis.call('zrank', KEYS[1], ARGV[1]))
if start == nil then return results end
while (#results <= count) do
    local zrange = redis.call('zrange', KEYS[1], start, start+rangelen-1)
    start = start + rangelen
    if (zrange == nil or #zrange == 0) then break end
    for i=1,#zrange do
        local entry = zrange[i]
        local minlen = math.min(#entry, #ARGV[1])
        if (string.sub(entry, 0, minlen) ~= string.sub(ARGV[1], 0, minlen)) then
            count = #results
            break
        end
        if (string.sub(entry, #entry, #entry) == '*') and (#results ~= count) then
            table.insert(results, string.sub(entry, 0, #entry-1))
        end
    end
end
return results
"""

if len(sys.argv) == 2 and sys.argv[1] == "--flush":
    print "Deleteing 'compl' key"
    r.delete('compl')

if not r.exists("compl"):
    t0 = time.time()
    print "Loading entries in the Redis DB"

    names = open(filename, "r")

    # Loop through each line
    for line in names:

        # Skip comments in the input file
        if line[0] == "#":
            continue

        r.eval(adderscript, 1, "compl", line.strip())
    names.close()
    print "Loaded in ", time.time() - t0, " seconds"
else:
    print "NOT loading entries, there is already a 'compl' key"

def complete(r, prefix, count):
    t0 = time.time()
    ret = r.eval(completescript, 1, "compl", prefix, count)
    print "Found %i entries in %.4f seconds" % (len(ret), time.time() - t0)
    return ret

print complete(r, "ma", 50)
print complete(r, "zu", 50)
