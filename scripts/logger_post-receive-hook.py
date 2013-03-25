import cgi
import cgitb
import simplejson
from datetime import datetime

def get_commit_log(commit):
    """ Given a commit dict object return a log string """
    commit_sha = commit['id'] 
    commit_author = '{} ({}) <{}>'.format(commit['author']['name'], commit['author']['username'], commit['author']['email'])
    commit_timestamp = commit['timestamp']
    commit_message = commit['message']
    log_commit = '{}, {}, {}, "{}"'.format(commit_sha, commit_author, commit_timestamp, commit_message)
    
    return log_commit

""" Print HTTP Response """
print 'Content-Type: text/html'
print ''

print '<html>'
print '<head>'
print '<title>{}</title>'.format('GitHub Post Receive Hook')
print '<head>'
print '<body>'
print '<h1>{}</h1>'.format('GitHub Post Receive Hook')

""" Parse Input Arguments """
cgitb.enable()
args = cgi.FieldStorage()

""" Log Message Leading String """
call_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S%p %z')
log_message = ''

# Check if payload exists
if 'payload' not in args:
    log_message = '[ERROR {}] Invalid request. Missing JSON payload'.format(call_time)

else:
    # Attempt to reason payload as JSON object and parse.
    try:
        """ Log Message Contents """
        log_lead = '[LOG {}]'.format(call_time)
        payload = simplejson.loads(args['payload'].value)

        repo_org = payload['repository']['owner']['name']
        repo_name = payload['repository']['name']
        log_repo = '[{}/{}]'.format(repo_org, repo_name)

        commit_count = len(payload['commits'])
        
        # Treat multi-commit pushes with more care
        if commit_count > 1:
            commit_latest = payload['head_commit']['id']
            log_message = '{}{} Push with {} commits. Latest {}'.format(log_lead, log_repo, commit_count, commit_latest)
            for c in payload['commits']:
                single_commit = get_commit_log(c)
                log_message += '\n{}{} {}'.format(log_lead, log_repo, single_commit)

        else:
            log_commit = get_commit_log(payload['head_commit'])
            log_message = '{}{} {}'.format(log_lead, log_repo, log_commit)

        """ Write Ouput to File """
        logFileName = '{}_{}.log'.format(repo_org, repo_name)
        logFile = open(logFileName, 'a')
        logFile.writelines(log_message)
        logFile.writelines('\n\n')
        logFile.close()
        
    except ValueError:
        log_message = '[ERROR {}] Error Parsing JSON payload'.format(call_time)


""" Write Ouput to HTML """
print '<pre>{}</pre>'.format(log_message)
print '</body>'
print '</html>'
