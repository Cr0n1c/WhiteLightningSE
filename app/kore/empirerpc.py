import json
import ssl
import urllib2

#TODO: Make shell its own command, so it changes context to shell?

cmd_rpc_map = {'help':{'help':'Lists available help, or gives you help on a specific command'},
               'rename':{'help':'Rename the current agent',
                         'url':'/api/agents/{AGENT_NAME}/rename',
                         'params':{'newname':'the name to rename the specified agent to (required)'}},
               'kill':{'help':'Kill the current agent',
                       'url':'/api/agents/{AGENT_NAME}/kill'}}
shell_cmd = {'help':'Any valid shell command (OS specific)',
             'url':'/api/agents/{AGENT_NAME}/shell',
             'params':{'command':'the shell command to task the agent to run (required)'}}
 
class EmpireRpc():
    '''
    The interface to EmpireRPC.  Instantiate an object with the agent to run it against.
    Then call handle_command() with the command line you want to run
    '''
                  
    def __init__(self,empire_ip,rest_port,username=None,password=None,apikey=None):
        self.ip = empire_ip
        self.port = rest_port
        if (username is None or password is None) and apikey is None:
            raise Exception("Username and password, or API key must be used")

        if apikey is not None:
            self.apikey = apikey
        else:
            self.username = username
            self.password = password
            self.renew_apikey()

    def renew_apikey(self):
        #Get apikey from empire
        # curl --insecure -i -H "Content-Type: application/json" https://localhost:1337/api/admin/login -X POST -d '{"username":"empireadmin", "password":"Password123!"}'
        #request
        if self.username is not None and self.password is not None:
            data = json.dumps({"username":self.username,"password":self.password})
            resp_json = self._send_request('api/admin/login',data=data,use_token=False)
            if resp_json is not None:
                self.apikey = resp_json.get('token')
                return True
            else:  
                return False

    def _send_request(self,api_path,data=None,use_token=True):
        '''
        Sends a request to EmpireRPC
        param string api_path The URI for the API call to make (e.g. api/agents/agent1/shell)
        param json_string data A JSON string of data to send with the request
        param use_token bool Toggles wether to append the apikey to the request or not
        return dict Key=Value pairs returned from request
        '''
        url = "https://{}:{}/{}".format(self.ip,self.port,api_path)
        if use_token:
            url = "{}?token={}".format(url,self.apikey)
        print url
        if data is None:
            req = urllib2.Request(url)
        else:
            req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        # TODO: Handle 404
        f = urllib2.urlopen(req, context=scontext)
        response = f.read()
        f.close()
        try:
            resp_json = json.loads(response)
            return resp_json
        except ValuesError:        
            return None

    def handle_command(self, command, agent_name=None):
        print command
        cmd = command.lower().split(' ',1)
        params = None
        if len(cmd) == 2:
            (cmd,params) = cmd
        else:
            cmd = cmd[0]
        if cmd in cmd_rpc_map.keys():
            func = getattr(self,'do_{}'.format(cmd),self.notimpl_cmd)
            return func(params=params,agent_name=agent_name)
        else:
            # Not a valid rpc call, must be a shell command?
            return self.do_shell(cmd,params=params,agent_name=agent_name)
    
    def do_help(self, params=None, **kwargs):
        if params is None:
            line = "=== Built-in Commands ===\n"
            line += "\n".join(["{}\t{}".format(cmd,items['help']) for cmd,items in cmd_rpc_map.items()])
            line += "\nOr enter any valid shell command"
        else:
            cmd = params.lower().split()[0]
            if cmd in cmd_rpc_map:
                line = "{} {}\n".format(cmd," ".join(["[{}]".format(param) for param in cmd_rpc_map[cmd].get('params',[])]))
                line += cmd_rpc_map[cmd].get('help','No help available for this command')
            else:
                line = "Unknown Command"
        return {'success':True,'message':line}

    def do_shell(self, cmd, params=None, agent_name=None, **kwargs):
        data = json.dumps({"command":"{} {}".format(cmd,params)})
        json_resp = self._send_request('api/agents/{}/shell'.format(agent_name),data=data)        
        # TODO: The response is just success if the tasking was a success, still need to get the result sometime
        return json_resp

    def notimpl_cmd(self, params=None):
        return {'success':False,'message':"Not Implemented Yet!"}
