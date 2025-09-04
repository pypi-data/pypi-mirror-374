from math import erf
from warnings import warn

import matplotlib as mpl
import numpy as np
from cycler import cycler
from matplotlib import colormaps as mcm, colors as mcolors

PALETTES = ("cb.rbscale", "cb.rainbow", "cb.huescale", "cb.solstice", "cb.bird", "cb.pregunta", "cb.iris", "cb.extreme_rainbow")
PALETTES_FULL = (*PALETTES,*tuple([i+"_r" for i in PALETTES]))

STYLES = {
    "solid" : (0, ()),
    "dashed" : (0, (5, 5)),
    "densely_dashed" : (0, (5, 1)),
    "loosely_dashed" : (0, (5, 10)),

    "dotted" : (0, (1, 5)),
    "densely_dotted" : (0, (1, 1)),
    "loosely_dotted" : (0, (1, 10)),

    "dashdotted" : (0, (3, 5, 1, 5)),
    "densely_dashdotted" : (0, (3, 1, 1, 1)),
    "loosely_dashdotted" : (0, (3, 10, 1, 10)),

    "dashdotdotted" : (0, (3, 5, 1, 5, 1, 5)),
    "densely_dashdotdotted" : (0, (3, 1, 1, 1, 1, 1)),
    "loosely_dashdotdotted" : (0, (3, 10, 1, 10, 1, 10)),
}

c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,c24,c25,c26,c27,c28,c29 = (
    '#E8ECFB',
    '#D9CCE3',
    '#D1BBD7',
    '#CAACCB',
    '#BA8DB4',
    '#AE76A3',
    '#AA6F9E',
    '#994F88',
    '#882E72',
    '#1965B0',
    '#437DBF',
    '#5289C7',
    '#6195CF',
    '#7BAFDE',
    '#4EB265',
    '#90C987',
    '#CAE0AB',
    '#F7F056',
    '#F7CB45',
    '#F6C141',
    '#F4A736',
    '#F1932D',
    '#EE8026',
    '#E8601C',
    '#E65518',
    '#DC050C',
    '#A5170E',
    '#72190E',
    '#42150A',
)

d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15,d16,d17,d18,d19,d20,d21,d22,d23,d24,d25,d26,d27,d28,d29,d30,d31,d32,d33,d34 = (
    '#E8ECFB',
    '#DDD8EF',
    '#D1C1E1',
    '#C3A8D1',
    '#B58FC2',
    '#A778B4',
    '#9B62A7',
    '#8C4E99',
    '#6F4C9B',
    '#6059A9',
    '#5568B8',
    '#4E79C5',
    '#4D8AC6',
    '#4E96BC',
    '#549EB3',
    '#59A5A9',
    '#60AB9E',
    '#69B190',
    '#77B77D',
    '#8CBC68',
    '#A6BE54',
    '#BEBC48',
    '#D1B541',
    '#DDAA3C',
    '#E49C39',
    '#E78C35',
    '#E67932',
    '#E4632D',
    '#DF4828',
    '#DA2222',
    '#B8221E',
    '#95211B',
    '#721E17',
    '#521A13',
)


class Colorplots:
    def cblind(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        prop_cycle = mpl.rcParams['axes.prop_cycle']
        clist = prop_cycle.by_key()['color']
        if(ncurves<=4):
            colorscheme = ['#4477AA','#CC6677','#DDCC77','#117733']
        elif(ncurves>4 and ncurves<=12):
            colorscheme = ['#332288','#88CCEE','#117733','#DDCC77','#CC6677','#AA4499','#44AA99','#999933','#882255','#661100','#6699CC','#AA4466']
        elif(ncurves>12 and ncurves<=156):
            colorscheme = ['#332288','#88CCEE','#117733','#DDCC77','#CC6677','#AA4499','#44AA99','#999933','#882255','#661100','#6699CC','#AA4466']
            warn("out of range [1-12]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [1-156]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def contrast(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        prop_cycle = mpl.rcParams['axes.prop_cycle']
        clist = prop_cycle.by_key()['color']
        if(ncurves<=4):
            colorscheme = ['#000000','#004488','#BB5566','#DDAA33']
        elif(ncurves>4 and ncurves<=52):
            colorscheme = ['#000000','#004488','#BB5566','#DDAA33']
            warn("out of range [1-4]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [1-52]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def huescale(self, ncurves, *args, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        #SET DEFAULT VALUES IF NO OPTIONAL ARGUMENT
        prop_cycle = mpl.rcParams['axes.prop_cycle']
        clist = prop_cycle.by_key()['color']
        hue = "None"
        #OPTIONS
        possible_args = ("blue", "bluegreen", "green", "gold", "brown", "rose", "purple")
        for arg in args:
            if arg in possible_args:
                hue = arg
            else:
                raise NotImplementedError(
                    f"arg '{arg}' not implemented yet in huescale function"
                )

        if(ncurves<=3):
            if hue=='blue':
                colorscheme = ['#114477','#4477AA','#77AADD']
            if hue=='bluegreen':
                colorscheme = ['#117777','#44AAAA','#77CCCC']
            if hue=='green':
                colorscheme = ['#117744','#44AA77','#88CCAA']
            if hue=='gold':
                colorscheme = ['#777711','#AAAA44','#DDDD77']
            if hue=='brown':
                colorscheme = ['#774411','#AA7744','#DDAA77']
            if hue=='rose':
                colorscheme = ['#771122','#AA4455','#DD7788']
            if hue=='purple':
                colorscheme = ['#771155','#AA4488','#CC99BB']
            if hue=='None':
                colorscheme = ['#D95F0E','#FEC44F','#FFF7BC']
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])


        if(ncurves==4):
            colorscheme = ['#CC4C02','#FB9A29','#FED98E','#FFFBD5']
        if(ncurves==5):
            colorscheme = ['#993404','#D95F0E','#FB9A29','#FED98E','#FFFBD5']
        if(ncurves==6):
            colorscheme = ['#993404','#D95F0E','#FB9A29','#FEC44F','#FEE391','#FFFBD5']
        if(ncurves==7):
            colorscheme = ['#8C2D04','#CC4C02','#EC7014','#FB9A29','#FEC44F','#FEE391','#FFFBD5']
        if(ncurves==8):
            colorscheme = ['#8C2D04','#CC4C02','#EC7014','#FB9A29','#FEC44F','#FEE391','#FFF7BC','#FFFFE5']
        if(ncurves==9):
            colorscheme = ['#662506','#993404','#CC4C02','#EC7014','#FB9A29','#FEC44F','#FEE391','#FFF7BC','#FFFFE5']
        if(ncurves>3 and ncurves<=9 and hue!='None'):
            warn("only ocherscale for more than 3 plots", stacklevel=2)
        if(ncurves>9):
            colorscheme = clist
            warn("out of range [1-9]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def rbscale(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        prop_cycle=mpl.rcParams['axes.prop_cycle']
        clist=prop_cycle.by_key()['color']

        if(ncurves==3):
            colorscheme = ['#99C7EC','#FFFAD2','#F5A275']
        elif(ncurves==4):
            colorscheme = ['#008BCE','#B4DDF7','#F9BD7E','#D03232']
        elif(ncurves==5):
            colorscheme = ['#008BCE','#B4DDF7','#FFFAD2','#F9BD7E','#D03232']
        elif(ncurves==6):
            colorscheme = ['#3A89C9','#99C7EC','#E6F5FE','#FFE3AA','#F5A275','#D24D3E']
        elif(ncurves==7):
            colorscheme = ['#3A89C9','#99C7EC','#E6F5FE','#FFFAD2','#FFE3AA','#F5A275','#D24D3E']
        elif(ncurves==8):
            colorscheme = ['#3A89C9','#77B7E5','#B4DDF7','#E6F5FE','#FFE3AA','#F9BD7E','#ED875E','#D24D3E']
        elif(ncurves==9):
            colorscheme = ['#3A89C9','#77B7E5','#B4DDF7','#E6F5FE','#FFFAD2','#FFE3AA','#F9BD7E','#ED875E','#D24D3E']
        elif(ncurves==10):
            colorscheme = ['#3D52A1','#3A89C9','#77B7E5','#B4DDF7','#E6F5FE','#FFE3AA','#F9BD7E','#ED875E','#D24D3E','#AE1C3E']
        elif(ncurves==11):
            colorscheme = ['#3D52A1','#3A89C9','#77B7E5','#B4DDF7','#E6F5FE','#FFFAD2','#FFE3AA','#F9BD7E','#ED875E','#D24D3E','#AE1C3E']
        elif(ncurves>11 and ncurves<=143):
            colorscheme = ['#3D52A1','#3A89C9','#77B7E5','#B4DDF7','#E6F5FE','#FFFAD2','#FFE3AA','#F9BD7E','#ED875E','#D24D3E','#AE1C3E']
            warn("out of range [3-11]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [3-11]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def rainbow(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        prop_cycle=mpl.rcParams['axes.prop_cycle']
        clist=prop_cycle.by_key()['color']

        if(ncurves==4):
            colorscheme = ['#404096','#57A3AD','#DEA73A','#D92120']
        elif(ncurves==5):
            colorscheme = ['#404096','#529DB7','#7DB874','#E39C37','#D92120']
        elif(ncurves==6):
            colorscheme = ['#404096','#498CC2','#63AD99','#BEBC48','#E68B33','#D92120']
        elif(ncurves==7):
            colorscheme = ['#781C81','#3F60AE','#539EB6','#6DB388','#CAB843','#E78532','#D92120']
        elif(ncurves==8):
            colorscheme = ['#781C81','#3F56A7','#4B91C0','#5FAA9F','#91BD61','#D8AF3D','#E77C30','#D92120']
        elif(ncurves==9):
            colorscheme = ['#781C81','#3F4EA1','#4683C1','#57A3AD','#6DB388','#B1BE4E','#DFA53A','#E7742F','#D92120']
        elif(ncurves==10):
            colorscheme = ['#781C81','#3F479B','#4277BD','#529DB7','#62AC9B','#86BB6A','#C7B944','#E39C37','#E76D2E','#D92120']
        elif(ncurves==11):
            colorscheme = ['#781C81','#404096','#416CB7','#4D95BE','#5BA7A7','#6EB387','#A1BE56','#D3B33F','#E59435','#E6682D','#D92120']
        elif(ncurves==12):
            colorscheme = ['#781C81','#413B93','#4065B1','#488BC2','#55A1B1','#63AD99','#7FB972','#B5BD4C','#D9AD3C','#E68E34','#E6642C','#D92120']
        elif(ncurves>12 and ncurves<=156):
            colorscheme = ['#781C81','#413B93','#4065B1','#488BC2','#55A1B1','#63AD99','#7FB972','#B5BD4C','#D9AD3C','#E68E34','#E6642C','#D92120']
            warn("out of range [4-12]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [4-12]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def extreme_rainbow(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        prop_cycle=mpl.rcParams['axes.prop_cycle']
        clist=prop_cycle.by_key()['color']

        if(ncurves==1):
            colorscheme = [c10]
        elif(ncurves==2):
            colorscheme = [c10,c26]
        elif(ncurves==3):
            colorscheme = [c10,c18,c26]
        elif(ncurves==4):
            colorscheme = [c10,c15,c18,c26]
        elif(ncurves==5):
            colorscheme = [c10,c14,c15,c18,c26]
        elif(ncurves==6):
            colorscheme = [c10,c14,c15,c17,c18,c26]
        elif(ncurves==7):
            colorscheme = [c9,c10,c14,c15,c17,c18,c26]
        elif(ncurves==8):
            colorscheme = [c9,c10,c14,c15,c17,c18,c23,c26]
        elif(ncurves==9):
            colorscheme = [c9,c10,c14,c15,c17,c18,c23,c26,c28]
        elif(ncurves==10):
            colorscheme = [c9,c10,c14,c15,c17,c18,c21,c24,c26,c28]
        elif(ncurves==11):
            colorscheme = [c9,c10,c12,c14,c15,c17,c18,c21,c24,c26,c28]
        elif(ncurves==12):
            colorscheme = [c3,c6,c9,c10,c12,c14,c15,c17,c18,c21,c24,c26]
        elif(ncurves==13):
            colorscheme = [c3,c6,c9,c10,c12,c14,c15,c16,c17,c18,c21,c24,c26]
        elif(ncurves==14):
            colorscheme = [c3,c6,c9,c10,c12,c14,c15,c16,c17,c18,c20,c22,c24,c26]
        elif(ncurves==15):
            colorscheme = [c3,c6,c9,c10,c12,c14,c15,c16,c17,c18,c20,c22,c24,c26,c28]
        elif(ncurves==16):
            colorscheme = [c3,c5,c7,c9,c10,c12,c14,c15,c16,c17,c18,c20,c22,c24,c26,c28]
        elif(ncurves==17):
            colorscheme = [c3,c5,c7,c8,c9,c10,c12,c14,c15,c16,c17,c18,c20,c22,c24,c26,c28]
        elif(ncurves==18):
            colorscheme = [c3,c5,c7,c8,c9,c10,c12,c14,c15,c16,c17,c18,c20,c22,c24,c26,c27,c28]
        elif(ncurves==19):
            colorscheme = [c2,c4,c5,c7,c8,c9,c10,c12,c14,c15,c16,c17,c18,c20,c22,c24,c26,c27,c28]
        elif(ncurves==20):
            colorscheme = [c2,c4,c5,c7,c8,c9,c10,c11,c13,c14,c15,c16,c17,c18,c20,c22,c24,c26,c27,c28]
        elif(ncurves==21):
            colorscheme = [c2,c4,c5,c7,c8,c9,c10,c11,c13,c14,c15,c16,c17,c18,c19,c21,c23,c25,c26,c27,c28]
        elif(ncurves==22):
            colorscheme = [c2,c4,c5,c7,c8,c9,c10,c11,c13,c14,c15,c16,c17,c18,c19,c21,c23,c25,c26,c27,c28,c29]
        elif(ncurves==23):
            colorscheme = [c1,c2,c4,c5,c7,c8,c9,c10,c11,c13,c14,c15,c16,c17,c18,c19,c21,c23,c25,c26,c27,c28,c29]
        elif(ncurves>23 and ncurves<=34):
            colorscheme = [d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15,d16,d17,d18,d19,d20,d21,d22,d23,d24,d25,d26,d27,d28,d29,d30,d31,d32,d33,d34]
        elif(ncurves>34 and ncurves<=442):
            colorscheme = [d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13,d14,d15,d16,d17,d18,d19,d20,d21,d22,d23,d24,d25,d26,d27,d28,d29,d30,d31,d32,d33,d34]
            warn("out of range [1-34]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [1-34]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def solstice(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        prop_cycle=mpl.rcParams['axes.prop_cycle']
        clist=prop_cycle.by_key()['color']
        if(ncurves<=11):
            colorscheme = ['#364B9A','#4A7BB7','#6EA6CD','#98CAE1','#C2E4EF','#EAECCC','#FEDA8B','#FDB366','#F67E4B','#DD3D2D','#A50026']
        elif(ncurves>11 and ncurves<=143):
            colorscheme = ['#364B9A','#4A7BB7','#6EA6CD','#98CAE1','#C2E4EF','#EAECCC','#FEDA8B','#FDB366','#F67E4B','#DD3D2D','#A50026']
            warn("out of range [1-11]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [1-11]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def bird(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        prop_cycle=mpl.rcParams['axes.prop_cycle']
        clist=prop_cycle.by_key()['color']
        if(ncurves<=9):
            colorscheme = ['#2166AC','#4393C3','#92C5DE','#D1E5F0','#F7F7F7','#FDDBC7','#F4A582','#D6604D','#B2182B']
        elif(ncurves>9 and ncurves<=117):
            colorscheme = ['#2166AC','#4393C3','#92C5DE','#D1E5F0','#F7F7F7','#FDDBC7','#F4A582','#D6604D','#B2182B']
            warn("out of range [1-9]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [1-9]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def pregunta(self, ncurves, *, update_prop_cycle=True):
        stylescheme = [STYLES[key] for key in list(STYLES.keys())]
        # stylescheme = [STYLES["solid"]]*ncurves
        prop_cycle=mpl.rcParams['axes.prop_cycle']
        clist=prop_cycle.by_key()['color']
        if(ncurves<=9):
            colorscheme = ['#762A83','#9970AB','#C2A5CF','#E7D4E8','#F7F7F7','#D9F0D3','#ACD39E','#5AAE61','#1B7837']
        elif(ncurves>9 and ncurves<=117):
            colorscheme = ['#762A83','#9970AB','#C2A5CF','#E7D4E8','#F7F7F7','#D9F0D3','#ACD39E','#5AAE61','#1B7837']
            warn("out of range [1-9]: changed the linestyle", stacklevel=2)
        else:
            colorscheme = clist
            warn("out of range [1-9]: colorblind mode deactivated", stacklevel=2)

        if update_prop_cycle:
            mpl.rcParams['axes.prop_cycle'] = cycler('linestyle', stylescheme[0:ncurves])*cycler('color', colorscheme[0:ncurves])
        return(colorscheme, stylescheme)

    def monocolor(self, ncurves, *args):
        possible_args = ("b&w", "blue", "red", "yellow", "green", "purple")
        printing = "b&w"
        for arg in args:
            if arg in possible_args:
                printing = arg
            else:
                raise NotImplementedError(
                    f"arg '{arg}' not implemented yet in monocolor function"
                )

        if (printing=='b&w'):
            colorscheme=['black']*ncurves
        if (printing=='blue'):
            colorscheme=['#4477AA']*ncurves
        if (printing=='red'):
            colorscheme=['#CC6677']*ncurves
        if (printing=='yellow'):
            colorscheme=['#DDCC77']*ncurves
        if (printing=='green'):
            colorscheme=['#117733']*ncurves
        if (printing=='purple'):
            colorscheme=['#771155']*ncurves

        if printing in possible_args:
            stylescheme = [
                STYLES["solid"],
                STYLES["dashed"],
                STYLES["dotted"],
                STYLES["dashdotted"],
                STYLES["dashdotdotted"],
                STYLES["densely_dashed"],
                STYLES["densely_dotted"],
                STYLES["densely_dashdotted"],
                STYLES["densely_dashdotdotted"],
                STYLES["loosely_dashed"],
                STYLES["loosely_dotted"],
                STYLES["loosely_dashdotted"],
                STYLES["loosely_dashdotdotted"],
            ]
            if(ncurves>13):
                warn("maximum 13 different linestyles", stacklevel=2)
                stylescheme = stylescheme*int(np.ceil(ncurves/13))
            stylescheme = stylescheme[0:ncurves]
            default_cycler=(cycler(color=colorscheme)+cycler(linestyle=stylescheme))
            mpl.rc('axes', prop_cycle=default_cycler)
        return(colorscheme,stylescheme)

def reversed_cmap(cmap, name = 'my_cmap_r', nbin=None):
    warn(
        "cblind.reversed_cmap(cm, ...) is deprecated. "
        "Please use cm.reversed() instead. ",
        category=DeprecationWarning,
        stacklevel=2,
    )
    if nbin is None:
        nbin=256
    reverse = []
    k = []

    for key in cmap._segmentdata:
        k.append(key)
        channel = cmap._segmentdata[key]
        data = []
        for t in channel:
            data.append((1-t[0],t[2],t[1]))
        reverse.append(sorted(data))

    LinearL = dict(zip(k, reverse, strict=True))
    my_cmap_r = mcolors.LinearSegmentedColormap(name, LinearL, N=nbin)
    return my_cmap_r


_REGISTERED = set()
def _register_to_mpl(name):
    if name in _REGISTERED:
        return
    cbcmap = _get_cbmap(name)

    mcm.register(cbcmap)
    mcm.register(cbcmap.reversed())
    _REGISTERED.add(name)

def _erf_vector(arr):
    # a simple substitute for scipy.special.erf
    # performance is about 1/20 with respect to scipy impl
    # but results are still obtained within well below 1ms for 256 elements
    # which is the typical application
    out = np.empty_like(arr)
    out[:] = [erf(_) for _ in arr]
    return out

def _get_cbmap(palette, nbin=256):
    x=np.linspace(0.,1.,nbin)
    if palette not in PALETTES_FULL:
        raise NotImplementedError(
            f"palette '{palette}' not implemented yet in _get_cbmap function"
        )
    palette_tmp = palette
    if palette[-2:]=="_r":
        palette_tmp = palette[:-2]

    if palette_tmp=="cb.rbscale":
        red=0.237-2.13*x+26.92*x**2-65.5*x**3+63.5*x**4-22.36*x**5
        green=((0.572+1.524*x-1.811*x**2)/(1.-0.291*x+0.1574*x**2))**2
        blue=(1./(1.579-4.03*x+12.92*x**2-31.4*x**3+48.6*x**4-23.36*x**5))
    elif palette_tmp=='cb.rainbow':
        red = (0.472-0.567*x+4.05*x**2)/(1.+8.72*x-19.17*x**2+14.1*x**3)
        green = 0.108932-1.22635*x+27.284*x**2-98.577*x**3+163.3*x**4-131.395*x**5+40.634*x**6
        blue = 1./(1.97+3.54*x-68.5*x**2+243*x**3-297*x**4+125*x**5)
    elif palette_tmp=='cb.huescale':
        red = 1.-0.392*(1.+_erf_vector((x-0.869)/0.255))
        green = 1.021-0.456*(1.+_erf_vector((x-0.527)/0.376))
        blue = 1.-0.493*(1.+_erf_vector((x-0.272)/0.309))

    if palette_tmp=="cb.rbscale" or palette_tmp=="cb.rainbow" or palette_tmp=="cb.huescale":
        redline = np.empty((len(x), 3))
        greenline = np.empty((len(x), 3))
        blueline = np.empty((len(x), 3))

        redline[:, 0] = greenline[:, 0] = blueline[:, 0] = x
        redline[:, 1] = redline[:, 2] = red
        greenline[:, 1] = greenline[:, 2] = green
        blueline[:, 1] = blueline[:, 2] = blue

        cdict = {'red':   redline,
                 'green': greenline,
                 'blue': blueline}

        cbcmap = mcolors.LinearSegmentedColormap(f"{palette_tmp}", cdict, N=nbin)
    elif palette_tmp=="cb.extreme_rainbow":
        cbcmap = mcolors.LinearSegmentedColormap.from_list(f"{palette_tmp}", Colorplots().extreme_rainbow(34, update_prop_cycle=False)[0], N=nbin)
    elif palette_tmp=="cb.solstice":
        cbcmap = mcolors.LinearSegmentedColormap.from_list(f"{palette_tmp}", Colorplots().solstice(11, update_prop_cycle=False)[0], N=nbin)
    elif palette_tmp=="cb.bird":
        cbcmap = mcolors.LinearSegmentedColormap.from_list(f"{palette_tmp}", Colorplots().bird(9, update_prop_cycle=False)[0], N=nbin)
    elif palette_tmp=="cb.pregunta":
        cbcmap = mcolors.LinearSegmentedColormap.from_list(f"{palette_tmp}", Colorplots().pregunta(9, update_prop_cycle=False)[0], N=nbin)
    elif palette_tmp=="cb.iris":
        cmap_iris = ["#FEFBE9", "#FCF7D5", "#F5F3C1", "#EAF0B5", "#DDECBF", "#D0E7CA", "#C2E3D2", "#B5DDD8", "#A8D8DC", "#9BD2E1", "#8DCBE4", "#81C4E7", "#7BBCE7", "#7EB2E4", "#88A5DD", "#9398D2", "#9B8AC4", "#9D7DB2", "#9A709E", "#906388", "#805770", "#684957", "#46353A"]
        cbcmap = mcolors.LinearSegmentedColormap.from_list(f"{palette_tmp}", cmap_iris, N=nbin)
    if palette[-2:]=="_r":
        cbcmap = cbcmap.reversed()
    return(cbcmap)

def cbmap(palette=None, nbin=256):
    warn(
        "cblind.cbmap is deprecated. "
        "Please use matplotlib.colormaps.get_cmap instead, or "
        "matplotlib.pyplot.get_cmap if you need to specify nbin "
        "(default is 256)",
        category=DeprecationWarning,
        stacklevel=2,
    )
    if palette in PALETTES_FULL:
        return _get_cbmap(palette, nbin)
    else:
        import matplotlib.pyplot as plt

        return plt.get_cmap(palette, nbin)


def mapping(fig, ax, data2d, palette=None, nbin=None):
    if nbin is None:
        cmap = mcm.get_cmap(palette)
    else:
        import matplotlib.pyplot as plt

        cmap = plt.get_cmap(palette, nbin)

    im=ax.imshow(data2d, cmap=cmap, aspect='auto')
    fig.colorbar(im)

def test_cblind(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().cblind(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=1.5)

    plt.show()

def test_contrast(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().contrast(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=1.5)

    plt.show()

def test_huescale(ny, *args):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().huescale(ny, *args)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=2.0)

    plt.show()

def test_rbscale(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().rbscale(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=2.0)

    plt.show()

def test_solstice(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().solstice(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=2.0)

    plt.show()

def test_bird(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().bird(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=2.0)

    plt.show()

def test_pregunta(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().pregunta(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=2.0)

    plt.show()

def test_rainbow(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().rainbow(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=2.0)

    plt.show()

def test_extreme_rainbow(ny):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().extreme_rainbow(ny)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=2.0)

    plt.show()

def test_monocolor(ny, *args):
    import matplotlib.pyplot as plt

    nx=100
    x=np.linspace(0,10, nx)
    y=np.zeros((ny,nx), dtype=int)
    color, linestyle = Colorplots().monocolor(ny, *args)

    fig, ax = plt.subplots()
    for i in range(ny):
        for j in range(nx):
            y[i][j]=x[j]+i
        # plt.plot(x,y[i], color[i], linewidth=2.0)
        ax.plot(x,y[i], linewidth=1.0)

    plt.show()

def test_mapping(palette=None,nbin=None):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    r = np.arange(-np.pi, np.pi, 0.1)
    t = np.arange(0, 2*np.pi, 0.1)
    X, Y = np.meshgrid(r, t)
    data = np.cos(X) * np.sin(Y) * 10

    mapping(fig, ax, data, palette=palette, nbin=nbin)
    plt.show()
