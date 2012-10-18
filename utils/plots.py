import matplotlib.pyplot as plt
from matplotlib.patches import Circle as circ
from numpy import *
import numpy as np
import matplotlib.patches as patches
import everySNAKE.config as cfg
import inspect, os


class tmpF(object):
    def __init__(self,num = 10, size = (8,8)):
        self.f = fignum(num)
        self.num = num

    def save(self):
        savepath = cfg.dataPath('figs/tmp/tmp_fig_{0}.pdf').format(self.num)
        self.f.savefig(savepath)
        

def fignum(num, size = (8,8)):
    plt.close(num)
    return plt.figure(num, size)


def figpath(filename = 'plot.pdf', delete = False):
    called_name = inspect.stack()[1][3]
    stack = inspect.stack()[1]
    call_path = os.path.abspath(stack[1])
    path = cfg.relPath(call_path)
    figpath = cfg.dataPath(os.path.join('figs',path,called_name,filename))
    if delete:
        if os.path.isfile(figpath):
            os.remove(figpath)
    return figpath
    

def color_legend(fig,colors, labels,
                 frameon = False,
                 markersize = 40,
                 pos = 0,
                 ax = None):
    n = len(colors)
    patches = []

    if not ax:
        dax = fig.add_axes([0,0,.1,.1])
        dax.set_visible(False)
        trg = fig
    else:
        trg = ax

    for i in range(n):
        c = colors[i]
        l = labels[i]
        patches.append(circ((0,0),1,
                         ec = 'none',
                         fc = c,
                         ))
    
    trg.legend(patches,
               labels,pos,
               frameon = frameon,prop = {'family':'serif'},
               fancybox = True
               )

def hideaxes(ax, visible = False):
    ax.get_yaxis().set_visible(visible)
    ax.get_xaxis().set_visible(visible)

def maketitle(ax, title, subtitle = None,alpha = 1):
    ax.annotate(title,[.05,.97],
                xycoords = 'axes fraction',
                verticalalignment = 'top',
                size = 'x-large',
                alpha = alpha
                )
    if subtitle:
        ax.annotate(subtitle, [.05,.97],
                    size = 'large',
                    xycoords = 'figure fraction',
                    xytext = [0,-5],
                    textcoords = 'offset points'
                    ,verticalalignment = 'top',
                    alpha = alpha)

def label_lr(ax, label):
    ax.annotate(label,[.95,.05],xycoords = 'axes fraction',
                verticalalignment = 'bottom',
                horizontalalignment = 'right',
                size = 'large')


def scatter_backdrop(fig,colors):
    #nx: number of cells in each dimensions
    #colors: nx*nx array of colors

    
    nx = shape(colors)[1]
    ny = shape(colors)[0]


    ax = fig.add_axes([0,0,1,1])
    ax.autoscale(False)
    ax.set_xlim([0,nx - 1])
    ax.set_ylim([0,ny - 1])
    
    hideaxes(ax)
    ax.set_aspect('auto')
    #pritn 'axas'
    ax.imshow(colors, interpolation = 'nearest',aspect = 'auto')
    #for i in range(nx):
    #    for j in range(ny):
    #        xy = array([[float(i)/nx,float(i+1)/nx],[ float(j)/nx,float(j+1)/nx]])
    #        color= colors[i,j]
    #        polyxy = array([xy[0][[0,1,1,0]],xy[0][[0,0,1,1]]]).T
    #        rpatch = patches.Rectangle(xy[:,0],1.0/nx,1.0/nx,
    #                                 color = color)
    #        ax.add_patch(rpatch)
            

def scatter_relations(fig,xvals, yvals):
    pass


def draw_pb(ax, net):
    mods = net.modules
    mnames = [x.name for x in mods]
    mlayers = None

    ins = []
    hids = []
    outs = []

    for m in mods:
        if m in net.inmodules:
            ins.append(m)
        elif m in net.outmodules:
            outs.append(m)
        else:
            hids.append(m)
  
    ins = sorted(ins,key = lambda x: x.name)
    outs = sorted(outs,key = lambda x: x.name)
    hids = sorted(hids,key = lambda x: x.name)

    mod_infos = {}
    for i in range(3):
        mlist = [ins,hids,outs][i]
        for j in range(len(mlist)):
            info = {'x':i,'y':j,'num':mlist[j].dim}
            mod_infos[mlist[j].name] = info


    cxn_details = []
    cxns = net.connections
    for these_cxns in cxns.values():
        for c in these_cxns:
            if len(c.params) > 1:
                raise Exception("don't know how to draw")
            
            cxn_details.append({'im':c.inmod.name,
                                'om':c.outmod.name,
                                'iidx':c.inSliceFrom,
                                'oidx':c.outSliceFrom,
                                'weight':c.params[0]})
            


    #SOME ACTUAL DRAWING!

    max_w = max(map(lambda x: x['weight'],cxn_details))
    color_lam = lambda x: x > 0 and 'red' or 'blue'
    alpha_lam = lambda x: abs(x)/max_w
    
    axheight = 1
    mfracs = array([.8/len(ins),.8/len(hids),.8/len(outs)])
    xfrac = .33
    get_y = lambda x: (x['y']+.5)* mfracs[x['x']]
    get_x = lambda x: (x['x']+.5)* xfrac
    get_idx_ofs = lambda idx,x:(float(idx +.5)/x['num'] -.5) *.5* mfracs[x['x']] 
    
    
    shrt = True
    def get_lab(x):
        if not shrt:
            tflabs = ['shared TFs'] + ['g' + str(i) +' solo TFs' for i in range(len(outs))] 
            hlabs = ['shared'] + ['g' + str(i)+ ' hidden unit' for i in range(len(outs))] 
            glabs = ['g' + str(i)+ ' expr level' for i in range(len(outs))]
        else:
            tflabs = ['Shared_TFs'] + ['g' + str(i) for i in range(len(outs))] 
            hlabs = ['Bias'] + ['g' + str(i) for i in range(len(outs))] 
            glabs = ['g' + str(i) for i in range(len(outs))]
            
        if x['x'] == 0:
            return tflabs[x['y']]
        if x['x'] == 2:
            return glabs[x['y']]
        return hlabs[x['y']]
    
    node_r = 10
    mod_r = 50
    nxs,nys,nas,ncs ,nalphas =  [ [] for i in range(5)]


    for m in mod_infos.values():
        nxs.append(get_x(m))
        nys.append(get_y(m))
        nas.append(power(mod_r,2))
        ncs.append([.9,.9,.9])
        nalphas.append(.25)
        ax.annotate( get_lab(m),[get_x(m),get_y(m)],
                     xytext = array([mod_r,mod_r])/2,textcoords = 'offset pixels'
                     ,size = 'large')

        for i in range(m['num']):
            xy = [get_x(m),get_y(m) + get_idx_ofs(i,m)]
            nxs.append(xy[0])
            nys.append(xy[1])
            nas.append(power(node_r,2) * pi)
            ncs.append('white')
            nalphas.append(1)


                  
    ax.scatter(nxs,nys,nas,alpha = .25, color = ncs, edgecolor = 'black')


    for c in cxn_details:
        imod = mod_infos[c['im']]
        omod = mod_infos[c['om']]

        ixy = [get_x(imod),get_y(imod) + get_idx_ofs(c['iidx'],imod)]
        hxy = [get_x(omod),get_y(omod) + get_idx_ofs(c['oidx'],omod)]

        p = patches.ConnectionPatch(ixy, hxy,'data','data',
                                    arrowstyle = 'wedge,tail_width=1.5',
                                    shrinkA =node_r +1,
                                    shrinkB =node_r +1,
                                    edgecolor = 'black',
                                    facecolor = 'none',
                                    alpha = 1)
        ax.add_patch(p)

        p = patches.ConnectionPatch(ixy, hxy,'data','data',
                                    arrowstyle = 'wedge,tail_width=1.5',
                                    shrinkA =node_r +3,
                                    shrinkB =node_r +3,
                                    edgecolor = 'none',
                                    facecolor = color_lam(c['weight']),
                                    alpha = alpha_lam(c['weight']))
        ax.add_patch(p)


    ax.set_ylim([0,1])
    ax.set_xlim([0,1])
    

def color_array(arr, maxabs = 1):
    maxabs = np.max(np.abs(arr))
    a2 = array(arr)
    a2/=maxabs

    slf = .75
    a2great = array([-1.0,-1.0,0.0])* ((a2* greater(a2,0      ))[:,:,newaxis])*slf
    a2less  = array([0.0,-1.0,-1.0])* ((-1*a2* less_equal(a2,0))[:,:,newaxis])*slf
    colors = array([1,1,1])[newaxis,newaxis,:] + a2great + a2less
    
    return colors

def colorscale(arr, rgb = False):
    '''Scale an array for plotting as an image
If rgb in on, rgb channels are normalized independently.
'''
    if not rgb:
        amax = np.max(arr)
        amin = np.min(arr)
        return (arr - amin)/(amax - amin)
    else:
        amax = np.max(np.max(arr,0),0)
        amin = np.min(np.min(arr,0),0)
        return (arr - amax)/(amax - amin)

def spacefill(ax,rs, cs):
  import compbio.utils.lilturtle as lt
  
  t = lt.lilturtle(90)
  l = len(rs)
  levs = t.inverseN(l)
  t.hilbert(levs)
  c = t.curve()

  xs = c[:l,0]
  ys = c[:l,1]

  ax.plot(xs,ys, zorder = -1, alpha = .2, color = 'black')
  ax.scatter(xs,ys,rs,color = cs)
def padded_limits(ax, xvals, yvals, margin = [.2,.2]):
    
    if len(shape(margin) )== 0:
        margin = [margin] * 2
    dx = max(xvals) - min(xvals)
    dy = max(yvals) - min(yvals)
    ax.set_autoscaley_on(False)
    ax.set_autoscalex_on(False)
    ax.set_xlim([min(xvals) - dx *margin[0], max(xvals) + dx * margin[0]])
    ax.set_ylim([min(yvals) - dy *margin[1], max(yvals) + dy * margin[1]])

def rescale(arr, lims):
    dl = lims[1] - lims[0]
    da = np.max(arr) - np.min(arr)
    print arr
    arr_out = array(arr)
    arr_out -= np.min(arr_out)
    arr_out /= da
    arr_out *= dl
    print dl, da
    arr_out += lims[0]
    return arr_out
