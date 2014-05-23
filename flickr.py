
import json, md5, urllib, httplib, webbrowser
from xml.dom.minidom import parseString

class SmartRecord(dict):
  def __init__(self, *args):
    dict.__init__(self, *args)
  def __getattr__(self, name):
    return self[name]
  def __setattr__(self, name, value):
    self[name] = value

def make_record(element):
  rec = SmartRecord()
  attributes = element.attributes
  if attributes is not None:
    for i in range(attributes.length):
      rec[attributes.item(i).name] = attributes.item(i).nodeValue
  for i in range(len(element.childNodes)):
    child = element.childNodes[i]
    if child.nodeType == child.TEXT_NODE:
      name = u'text'
      value = child.data
    else:
      name = child.tagName
      value = make_record(child)
    if name not in rec:
      rec[name] = value
    elif isinstance(rec[name], list):
      rec[name] = rec[name] + [value]
    else:
      rec[name] = [rec[name]] + [value]
  return rec

def make_record_for_xml(xml):
  #print xml
  dom = parseString(xml)
  element = dom.documentElement
  rec = make_record(element)
  dom.unlink()
  #print rec
  return rec

class FlickrError:
  def __init__(self, code, msg):
    self.code = int(code)
    self.msg = msg
  def __str__(self):
    return `self.code` + ': ' + self.msg

def sign(secret, **args):
  keys = args.keys()
  keys.sort()
  s = secret + ''.join([key + str(args[key]) for key in keys])
  return md5.new(s).hexdigest()

class FlickrFunction:
  def __init__(self, name, api_key, secret):
    self.name = name
    self.api_key = api_key
    self.secret = secret

  def __getattr__(self, name):
    return FlickrFunction(self.name + '.' + name, self.api_key, self.secret)

  def __call__(self, **args):
    args['api_key'] = self.api_key
    args['method'] = 'flickr.' + self.name
    args['api_sig'] = sign(self.secret, **args)
    url = 'http://www.flickr.com/services/rest/?'
    params = urllib.urlencode(args)
    url = url + params
    #print url
    xml = urllib.urlopen(url).read()
    rec = make_record_for_xml(xml)
    if rec['stat'] == 'fail':
      raise FlickrError(rec['err']['code'], rec['err']['msg'])
    return rec

class flickr:
  def __init__(self, api_key, secret):
    self.api_key = api_key
    self.secret = secret

  def login(self, frob):
    args = {
      'api_key': self.api_key,
      'frob': frob,
      'perms': 'write'
    }
    api_sig = sign(self.secret, **args)
    args['api_sig'] = api_sig
    url = 'http://flickr.com/services/auth/?' + urllib.urlencode(args)
    print 'You may need to go to:\n  ' + url
    webbrowser.open(url)
    print 'Press enter when done.'
    raw_input()

  def __getattr__(self,name):
    return FlickrFunction(name, self.api_key, self.secret)

  def upload(self, auth_token, photo, title, description, tags):
    args = {
      'api_key': self.api_key,
      'auth_token': str(auth_token),
      'title': title,
      'description': description,
      'tags': tags
    }
    api_sig = sign(self.secret, **args)
    args['api_sig'] = api_sig
    args['photo'] = photo
    boundary_num = 1
    boundary = "---------------------------"+`boundary_num`
    while boundary in photo:
      boundary_num = boundary_num+1
      boundary = "---------------------------"+`boundary_num`
    content = "--" + boundary + "\r\n"
    content = content + "Content-Disposition: form-data; name=\"api_key\"\r\n\r\n"
    content = content + args['api_key'] + "\r\n"
    content = content + "--" + boundary + "\r\n"
    content = content + "Content-Disposition: form-data; name=\"auth_token\"\r\n\r\n"
    content = content + args['auth_token'] + "\r\n"
    content = content + "--" + boundary + "\r\n"
    content = content + "Content-Disposition: form-data; name=\"api_sig\"\r\n\r\n"
    content = content + args['api_sig'] + "\r\n"
    content = content + "--" + boundary + "\r\n"
    content = content + "Content-Disposition: form-data; name=\"title\"\r\n\r\n"
    content = content + args['title'] + "\r\n"
    content = content + "--" + boundary + "\r\n"
    content = content + "Content-Disposition: form-data; name=\"description\"\r\n\r\n"
    content = content + args['description'] + "\r\n"
    content = content + "--" + boundary + "\r\n"
    content = content + "Content-Disposition: form-data; name=\"tags\"\r\n\r\n"
    content = content + args['tags'] + "\r\n"
    content = content + "--" + boundary + "\r\n"
    content = content + "Content-Disposition: form-data; name=\"photo\"; "
    content = content + "filename=\"/photo.jpg\"\r\n"
    content = content + "Content-Type: image/jpeg\r\n\r\n"
    content = content + photo
    content = content + "\r\n--" + boundary + "--\r\n\r\n"
    headers = {'Content-type': 'multipart/form-data; boundary='+boundary,
               'Content-length': `len(content)`,
               'Host': 'www.flickr.com'}
    conn = httplib.HTTPConnection('www.flickr.com')
    conn.request('POST', '/services/upload/', content, headers)
    response = conn.getresponse()
    xml = response.read()
    conn.close()
    dom = parseString(xml)
    element = dom.documentElement
    rec = make_record(element)
    dom.unlink()
    if rec['stat'] == 'fail':
      raise FlickrError(rec['err']['code'], rec['err']['msg'])
    return rec

try:
  config = json.loads(file('./config.json').read())
  api_key = config['api_key']
  secret = config['secret']
except IOError:
  print 'What is your api_key?'
  api_key = raw_input()
  print 'What is your secret?'
  secret = raw_input()
  file('./config.json', 'w').write(json.dumps({
    'api_key': api_key,
    'secret': secret,
  }))

flickr = flickr(api_key, secret)

