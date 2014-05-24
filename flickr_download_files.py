
import errno
import json
import os
import os.path
import urllib

try:
  os.mkdir("./flickr_photos")
except OSError, err:
  if err.errno != errno.EEXIST:
    raise

filenames = os.listdir("./flickr/")
total = len(filenames)

for i, filename in enumerate(filenames):
  print "File %d of %d" % (i, total)
  f = file("./flickr/" + filename)
  data = json.loads(f.read())
  print data["id"]
  if data.has_key("file"):
    if os.path.exists(data["file"]):
      continue

  url = data["url_o"]
  print url
  ext = url.split('.')[-1]
  image = urllib.urlopen(url).read()

  name2 = "./flickr_photos/" + data["id"] + "." + ext
  print name2
  f2 = file(name2, "wb")
  f2.write(image)
  f2.close()

  f = file("./flickr/" + filename, "w")
  data["file"] = name2
  f.write(json.dumps(data))
  f.close()

  print

