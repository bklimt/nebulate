
import errno
import json
import os

from flickr import flickr

try:
  os.mkdir("./flickr_photosets")
except OSError, err:
  if err.errno != errno.EEXIST:
    raise

def get_token_and_nsid():
  try:
    f = file('./auth.json')
    s = f.read()
    config = json.loads(s)
    if config['token'] and config['nsid']:
      return config['token'], config['nsid']
  except IOError:
    pass

  frob = flickr.auth.getFrob().frob.text
  flickr.login(frob)
  auth = flickr.auth.getToken(frob=frob).auth
  token = auth.token.text
  nsid = auth.user.nsid

  s = json.dumps({ 'token': token, 'nsid': nsid })
  f = file('./auth.json', 'w')
  f.write(s)

  return token, nsid

token, nsid = get_token_and_nsid()

status = flickr.people.getUploadStatus(auth_token=token).user
username = status.username.text
bandwidth_used = int(status.bandwidth.used)
bandwidth_max = int(status.bandwidth.max)
bandwidth_percent = bandwidth_used / (bandwidth_max*1.0)
print '%s: %s%%' % (username, bandwidth_percent*100)

photosets = flickr.photosets.getList(auth_token=token)
for photoset in photosets.photosets.photoset:
  print photoset.id
  f = file("./flickr_photosets/" + photoset.id + ".json", "w")
  f.write(json.dumps(photoset))
  f.close()

  pages = 1
  page = 1
  while page <= pages:
    photos = flickr.photosets.getPhotos(auth_token=token,
      photoset_id=photoset.id, page=page, per_page=500)
    for photo in photos.photoset.photo:
      f = file("./flickr/" + photo.id + ".json")
      data = json.loads(f.read())
      f.close()

      if not data.has_key("photosets"):
        data["photosets"] = []
      data["photosets"] = data["photosets"] + [photoset.id]
      
      f = file("./flickr/" + photo.id + ".json", "w")
      f.write(json.dumps(data))
      f.close()

      print "  " + photo.id
    page = page + 1

#  for photo in photos.photos.photo:
#    f = file('./flickr/' + photo.id + '.json', 'w')
#    f.write(json.dumps(photo))
#    f.close()

