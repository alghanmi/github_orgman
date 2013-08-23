import requests
import simplejson

""" GitHub Developer API v3:
        http://developer.github.com/v3/
"""

def github_request(method, url, payload=None, **kwargs):
	if method == 'get':
		print 'getRequest'
	elif method == 'put':
		print 'putRequest'
	elif method == 'post':
		print 'postRequest'

def github_get_request(url):
	github_request('get', url)

def github_post_request(url, payload):
	github_request('post', url, payload=payload)

def github_put_requst(url):
	github_request('put', url)

def gitHubGETRequest(url):
    ''' Return a dict with the result of this request '''
    r = requests.get(url, auth=(githubUsername, githubPassword))
    if r.status_code == 200:
        res = simplejson.loads(r.content)
        #pprint(res)
        return res
    else:
        print '[ERROR] Bad Request. Status Code', r.status_code
        return None

def gitHubPOSTRequest(url, payload):
    ''' Send a POST request to GitHub via API '''
    r = requests.post(url, data=simplejson.dumps(payload), auth=(githubUsername, githubPassword))
    res = simplejson.loads(r.content)
    #pprint(res)
    if r.status_code == 201:
        return res
    else:
        details = ''
        for e in res['errors']:
            details += '{}.{}: {}.'.format(e['resource'], e['field'], e['code'])
        print '[ERROR][HTTP {}] {} - {}'.format(r.status_code, res['message'], details)
        return None

def gitHub(url):
    ''' Send a PUT request to GitHub via API '''
    # http://developer.github.com/v3/orgs/teams/#add-team-member
    r = requests.put(url, auth=(githubUsername, githubPassword))
    if r.status_code == 204:
        return True
    else:
        res = simplejson.loads(r.content)
        pprint(res)
        details = ''
        if 'errors' in res:
            for e in res['errors']:
                details += '{}.{}: {}.'.format(e['resource'], e['field'], e['code'])
        print '[ERROR][HTTP {}] {} - {}'.format(r.status_code, res['message'], details)
        return False
