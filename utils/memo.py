'''
Write variables to common blocks and the hardrive to
increase efficiency of frequently called functions



#Basically, getorset can do three things
#  1: SET the stored value for the output of a function
#  2: GET the stored value for the output of function
#  3: UPDATE a new value without calling the function

'''


import inspect, os, pickle, cPickle
from numpy import *
from everySNAKE import config as cfg

#reset level constants
RESET_NONE=0
RESET_ONE_DEEP=2
RESET_ALL_DEEP=1
verbose_utils = True

 
def getOrSet(function, **kwargs):
  '''
The workhorse of the memo module.

Intended usage is basically:

-------

def getSomeComputedValue( [...=...], **kwargs):

  def setSomeComputedValue(**kwargs):
    ...
    [Do some expensive computation here]
    ...
    return [result of expensive computation]

  return memo.getOrSet(setSomeComputedValue,\
      **mem.rc(kwargs, 
               name=[some function of kwargs or other inputs],
               [...]
               ))

--------

Where memo.getOrSet simply serves to wrap and save output from  
setSomeComputedValue so that later calls to getSomeComputedValue 
will not have to recompute it.

KWARGS:
reset    [False] -   reset "function"
register ['a']   -   reserved spot for the current output in memory.
name     [register]- reserved sport for the current output on disk.
hardcopy [True]  -   save a hardcopy on disk.
np       [False] -   save data in an efficient numpy serialized form. (good for arrays)
update   [None]  -   if non-null, instead of calling function, use mock output
                     in update.
hard_reset [False]-  demand user input to actually reset the function.
                     (intended for tricky to compute functions)

'''
  reset = kwargs.get('reset', False)
  register = kwargs.get('register', 'a')
  name = kwargs.get('name',register)
  hardcopy = kwargs.get('hardcopy', True)
  np = kwargs.get('np', False)
  update = kwargs.get('update', None)
  on_fail = kwargs.get('on_fail', 'compute')
  hard_reset = kwargs.get('hard_reset', False)

  caller_name = inspect.stack()[1][3]

  
  
  if update != None:
    _write(name = name, value = update,  hardcopy = hardcopy, np = np,
          register = register, caller_name = caller_name)
  elif not reset:
    out, sxs = _read(name = name, hardcopy = hardcopy, np = np, 
                    register = register, caller_name = caller_name)
    if not sxs:
      if on_fail == 'compute': 
        print 'memo.py:\n  Fetch failed for {0}, name: {1}\n  "compute" flag is set'.\
            format(caller_name,name)
        reset = True
      else: assert 0, 'Data recovery failed for name ' + caller_name

  if reset:
    if hard_reset:
        user_inp = raw_input('''
This appears to be a hard function to compute ({0}:{1})
Really Reset? (y/n)
'''.format(caller_name, name))
        assert user_inp == 'y'

    out = function(**kwargs)
    _write(name = name, value = out,  hardcopy = hardcopy, np = np,
          register = register, caller_name = caller_name)
  return out
    



def claim_reset():
    if verbose_utils:
        print '''Resetting: \n{0}\n'''.format(inspect.stack()[1][3])



def reconcile(kw_new, kw_old = {}, **kwargs):
    '''
Reconcile new keywords into a kwargs object and check for any
forced resets in the active routine.
'''
    d0 = dict(kw_old)
    d0.update(kw_new)
    d0.update(kwargs)
    d0['reset'] = _make_reset_level(**d0)
    return d0

def sub_reconcile(kw_new, kw_old = {}, **kwargs):
    '''
Reconcile new keywords into a kwargs object and check for any
forced resets in the active routine. If reset_level is 2, set 
the reset level to zero in order to halt the reset cascade.
'''
    d0 = dict(kw_old)
    d0.update(kw_new)
    d0.update(kwargs)
    d0['reset'] = _make_sub_reset_level(**d0)
    return d0

sr = sub_reconcile 
rc = reconcile
 

def _write(name = None,value = None, hardcopy = True, np = False, 
          register= 'a', caller_name = None):
    if name == None: name = register
    if not caller_name: caller_name = inspect.stack()[1][3]
    savename = caller_name + '_' +name + '.memo'
 
    globals()['lastname_'+caller_name +register] = name
    globals()['last_'+caller_name+register] = value

    if hardcopy:
        path = os.path.join(cfg.getTempPath(), savename)
        f = open(path,'w')
        if np:
            save( f,value)
        else:
            pickle.dump(value, f)
        f.close()

def _read(name = None, hardcopy = True,np = False, 
         register = 'a', caller_name = None):
    if name == None: name = register
    sxs = False
    out = -1

    if not caller_name:caller_name = inspect.stack()[1][3]
    try:
        lname = globals()['lastname_'+caller_name+register]
        if lname == name or name == register:
            return globals()['last_'+caller_name+register], True
        else: 
            raise Exception()
    except Exception as e:
        if not hardcopy:
            return out, sxs
        savename = caller_name +'_'+name + '.memo'
        path =  os.path.join(cfg.getTempPath(),savename)

        if hardcopy:
            path = os.path.join(cfg.getTempPath(), savename)
            try:
              f = open(path,'r')
            except Exception as e:
              return out, sxs
            if np:
                out = load(f)
                sxs = True
            else:
                out = pickle.load( f)
                sxs = True
            f.close()

    
        globals()['lastname_'+caller_name +register] = name
        globals()['last_'+caller_name+register] = out

    return out, sxs




def _make_reset_level(**kwargs):
  '''Get the reset level for the current function'''
  reset = kwargs.get('reset', 0)
  if 'resets' in kwargs: 
    reset = kwargs['resets'].get( inspect.stack()[2][3], reset) 
    #raise Exception()
  return reset

def _make_sub_reset_level(**kwargs):
  reset = kwargs.get('reset', 0)
  if 'resets' in kwargs: 
    reset = kwargs['resets'].get( inspect.stack()[2][3], reset) 
  return mod(reset,2)
