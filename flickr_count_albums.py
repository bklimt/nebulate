
import errno
import json
import os
import urllib

filenames = os.listdir("./flickr/")
total = len(filenames)

hist = {}

for i, filename in enumerate(filenames):
  print "File %d of %d" % (i, total)
  f = file("./flickr/" + filename)
  data = json.loads(f.read())
  print data["id"]

  key = '0'
  if data.has_key("photosets"):
    key = str(len(data["photosets"]))

  if not hist.has_key(key):
    hist[key] = 0
  hist[key] = hist[key] + 1

print hist

