
import json
import os
import urllib

os.mkdir("./flickr_photos")

for filename in os.listdir("./flickr/"):
  f = file("./flickr/" + filename)
  data = json.loads(f.read())
  print data["id"]
  if data.has_key("file"):
    continue

  url = data["url_o"]
  print url
  ext = url.split('.')[-1]
  image = urllib.urlopen(url).read()

  name2 = "./flickr_photos/" + data["id"] + "." + ext
  print name2
  f2 = file(name2, "w")
  f2.write(image)
  f2.close()

  f = file("./flickr/" + filename, "w")
  data["file"] = name2
  f.write(json.dumps(data))
  f.close()

  print

