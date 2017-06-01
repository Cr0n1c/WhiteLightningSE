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
                  
    def __init__(self,agent_name=None):
        self.agent_name = agent_name

    def handle_command(self, command):
        print command
        cmd = command.lower().split(' ',1)
        params = None
        if len(cmd) == 2:
            (cmd,params) = cmd
        else:
            cmd = cmd[0]
        if cmd in cmd_rpc_map.keys():
            func = getattr(self,'do_{}'.format(cmd),self.notimpl_cmd)
            return func(params=params)
        else:
            # Not a valid rpc call, must be a shell command?
            return self.do_shell(cmd,params=params)
    
    def do_help(self, params=None):
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
        return line

    def do_shell(self, cmd, params=None):
        return "Shell commands not implemented yet!"

    def notimpl_cmd(self, params=None):
        return "Not Implemented Yet!"
