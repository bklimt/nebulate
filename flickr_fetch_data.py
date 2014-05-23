
from flickr import flickr
import json
import os

os.mkdir('./flickr')

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

page = 1
pages = 1

while page <= pages:
  print 'Fetching page %d of %d' % (page, pages)
  photos = flickr.people.getPhotos(auth_token=token, user_id=nsid, page=page,
    per_page=500, extras=','.join(['description', 'date_upload', 'date_taken',
    'original_format', 'last_update', 'geo', 'tags', 'machine_tags', 'o_dims',
    'views', 'media', 'url_o']))

  for photo in photos.photos.photo:
    f = file('./flickr/' + photo.id + '.json', 'w')
    f.write(json.dumps(photo))
    f.close()

  pages = int(photos.photos.pages)
  page = page + 1

