import sys,os,re
from abc import abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor
from type.model.Model import Model
from type.output.STDOut import STDOut
from sele.browser.Browser import Browser

class Behavior(Executor):
  def __init__(self,model:Model,browser:Browser=None)->None:
    super().__init__()
    self._meta = model.meta
    self._bizdata = model.bizdata
    self._config = model.config
    self._browser = browser
    
  def execute(self)->STDOut:
    key = 'target_CS_WE'
    if key in self._config and not self._config[key]:
      return STDOut(200,f'skip the behavior, the {key} is None')
    return self._invoke()
  
  @abstractmethod
  def _invoke(self):
    pass

  def _get_kwargs(self,keys:list[str],config=None)->dict:
    '''
    Extract specified keys from configuration dictionary
    @param {list[str]} keys: list of keys to extract from config
    @param {dict} config: optional config dict to merge with self._config (config takes precedence)
    @return {dict}: dictionary containing only the specified keys and their values
    '''
    conf = {**self._config,**config} if config else self._config
    # must remove the attr that value is None
    key_conf = {}
    for key in keys:
      if key in conf:
        key_conf[key] = conf.get(key)
    return key_conf
