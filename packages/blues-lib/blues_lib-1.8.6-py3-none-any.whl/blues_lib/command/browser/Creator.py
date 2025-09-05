import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from type.output.STDOut import STDOut
from sele.browser.BrowserFactory import BrowserFactory   
from namespace.CommandName import CommandName
from config.ConfigManager import config

class Creator(NodeCommand):

  NAME = CommandName.Browser.CREATOR
  TYPE = CommandName.Type.ACTION

  def _invoke(self)->STDOut:
    mode =  self._node_conf.get('mode')
    kwargs = self._node_conf.get('kwargs') or config.get('webdriver')
    browser = BrowserFactory(mode).create(**kwargs)
    return STDOut(200,'ok',browser) if browser else STDOut(500,'failed to create the browser')