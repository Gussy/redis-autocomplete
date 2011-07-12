redis-autocomplete
==================

What is this?
-------------
The two python scripts above both achieve the same results and are a port of the code provided 
by [antirez](http://antirez.com) in [this blog post](http://antirez.com/post/autocomplete-with-redis.html).

Usage
-----
`./redis-autocomplete.py [--flush]`
or
`./redis-autocomplete-scripted.py [--flush]`

If the database does not contain the `compl` key, all the female names from `female-names.txt` will be loaded into the database.
This can be forced optionally by adding the `--flush` argument, **however** this will flush the entire database, so use with caution.

Performance
-----------
On a [linode 360](http://linode.com) the scripting version loaded add the female names roughly *4x* as fast as the non scripted version.
Autocomplete lookups were also roughly *twice* as fast using the scripting version, although prefix input length affects this quite a bit.
