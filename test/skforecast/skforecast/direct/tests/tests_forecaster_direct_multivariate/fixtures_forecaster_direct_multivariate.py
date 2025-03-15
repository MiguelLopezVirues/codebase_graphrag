# Fixtures _forecaster_direct_multivariate
# ==============================================================================
import numpy as np
import pandas as pd

# Fixtures
# np.random.seed(123)
# l1 = np.random.rand(50)
# l2 = np.random.rand(50)
# exog_1 = np.random.rand(50)
series = pd.DataFrame(
             {'l1': pd.Series(
                        np.array(
                            [0.69646919, 0.28613933, 0.22685145, 0.55131477, 0.71946897,
                             0.42310646, 0.9807642 , 0.68482974, 0.4809319 , 0.39211752,
                             0.34317802, 0.72904971, 0.43857224, 0.0596779 , 0.39804426,
                             0.73799541, 0.18249173, 0.17545176, 0.53155137, 0.53182759,
                             0.63440096, 0.84943179, 0.72445532, 0.61102351, 0.72244338,
                             0.32295891, 0.36178866, 0.22826323, 0.29371405, 0.63097612,
                             0.09210494, 0.43370117, 0.43086276, 0.4936851 , 0.42583029,
                             0.31226122, 0.42635131, 0.89338916, 0.94416002, 0.50183668,
                             0.62395295, 0.1156184 , 0.31728548, 0.41482621, 0.86630916,
                             0.25045537, 0.48303426, 0.98555979, 0.51948512, 0.61289453]
                        )
                    ), 
              'l2': pd.Series(
                        np.array(
                            [0.12062867, 0.8263408 , 0.60306013, 0.54506801, 0.34276383,
                             0.30412079, 0.41702221, 0.68130077, 0.87545684, 0.51042234,
                             0.66931378, 0.58593655, 0.6249035 , 0.67468905, 0.84234244,
                             0.08319499, 0.76368284, 0.24366637, 0.19422296, 0.57245696,
                             0.09571252, 0.88532683, 0.62724897, 0.72341636, 0.01612921,
                             0.59443188, 0.55678519, 0.15895964, 0.15307052, 0.69552953,
                             0.31876643, 0.6919703 , 0.55438325, 0.38895057, 0.92513249,
                             0.84167   , 0.35739757, 0.04359146, 0.30476807, 0.39818568,
                             0.70495883, 0.99535848, 0.35591487, 0.76254781, 0.59317692,
                             0.6917018 , 0.15112745, 0.39887629, 0.2408559 , 0.34345601]
                        )
                    )
              }
         )
    
exog = pd.DataFrame(
           {'exog_1': pd.Series(
                          np.array(
                              [0.51312815, 0.66662455, 0.10590849, 0.13089495, 0.32198061,
                               0.66156434, 0.84650623, 0.55325734, 0.85445249, 0.38483781,
                               0.3167879 , 0.35426468, 0.17108183, 0.82911263, 0.33867085,
                               0.55237008, 0.57855147, 0.52153306, 0.00268806, 0.98834542,
                               0.90534158, 0.20763586, 0.29248941, 0.52001015, 0.90191137,
                               0.98363088, 0.25754206, 0.56435904, 0.80696868, 0.39437005,
                               0.73107304, 0.16106901, 0.60069857, 0.86586446, 0.98352161,
                               0.07936579, 0.42834727, 0.20454286, 0.45063649, 0.54776357,
                               0.09332671, 0.29686078, 0.92758424, 0.56900373, 0.457412  ,
                               0.75352599, 0.74186215, 0.04857903, 0.7086974 , 0.83924335]
                          )
                              ),
            'exog_2': ['a'] * 25 + ['b'] * 25}
       )

exog_predict = exog.copy()
exog_predict.index = pd.RangeIndex(start=50, stop=100)

data = pd.Series(
    data = np.array(
        [0.429795  , 0.410906  , 0.452159  , 0.522543  , 0.542369  ,
         0.652652  , 0.720119  , 0.40622   , 0.431348  , 0.469808  ,
         0.461801  , 0.520534  , 0.60338867, 0.60546342, 0.67476104,
         0.71860613, 0.75522329, 0.94125778, 0.9315028 , 0.57755434,
         0.62728322, 0.62389018, 0.64885882, 0.70012642, 0.74920969,
         0.808443  , 0.86151406, 0.9029471 , 0.97960539, 1.25308051,
         1.11932534, 0.7476698 , 0.82612127, 0.80049117, 0.85069626,
         0.89051379, 0.91811892, 1.04285206, 1.06589738, 1.07969198,
         1.14130358, 1.22330763, 1.22311257, 0.90525824, 0.9925723 ,
         0.97710782, 1.02124982, 1.05897764, 1.10313362, 1.23083723,
         1.22537176, 1.32580302, 1.33400947, 1.45665305, 1.47727594,
         1.07876165, 1.11933994, 1.14787166, 1.19492741, 1.18418877,
         1.30775844, 1.32950195, 1.36432369, 1.43485511, 1.42854235,
         1.6210894 , 1.50683354, 1.13382252, 1.16527317, 1.2180586 ,
         1.26233647, 1.2985704 , 1.38948036, 1.40799365, 1.50299549,
         1.54972374, 1.53052192, 1.76438934, 1.58054443, 1.28055721,
         1.32440799, 1.34664948, 1.37209054, 1.43336564, 1.52124538,
         1.52807535, 1.65489265, 1.6546239 , 1.6930087 , 1.8677323 ,
         1.79308148, 1.42269597, 1.57299589, 1.5039764 , 1.57923842,
         1.65387188, 1.73064824, 1.81618588, 1.87272889, 1.88789988,
         1.94728069, 2.06070727, 1.98965567, 1.60329151, 1.65850684,
         1.66899573, 1.72520922, 1.79652015, 1.93586494, 1.95598429,
         1.92524883, 2.06542102, 2.05859596, 2.14302442, 2.18380535,
         1.66064725, 1.83256901, 1.81847006, 1.88411469, 1.88943075,
         2.05192587, 2.1177052 , 2.08744447, 2.25429281, 2.34959022,
         2.26231323, 2.40586761, 1.84558438, 1.92116459, 1.96986207,
         2.0679384 , 2.06209591, 2.23806359, 2.25436753, 2.35319767,
         2.37697609, 2.36679597, 2.47277568, 2.45814487, 1.96829619,
         2.04333332, 2.07336735, 2.170516  , 2.23074564, 2.35636103,
         2.36688682, 2.54465893, 2.62064822, 2.53083821, 2.71323454,
         2.63012521, 2.17798867, 2.26901428, 2.26998602, 2.33512863,
         2.40680282, 2.56159317, 2.56486433, 2.714432  , 2.771011  ,
         2.816037  , 2.867238  , 2.79069   , 2.227639  , 2.29259   ,
         2.320505  , 2.355248  , 2.512263  , 2.554336  , 2.696497  ,
         2.794736  , 2.737043  , 2.869232  , 2.890712  , 2.970691  ,
         2.337135  , 2.466959  , 2.409641  , 2.587405  , 2.58797   ,
         2.684312  , 2.859648  , 2.815709  , 2.998253  , 2.948038  ,
         2.970053  , 3.083319  , 2.467753  , 2.584398  , 2.45176   ,
         2.645258  , 2.747934  , 2.874144  , 3.00821949, 3.05098161,
         3.05997914, 3.1235343 , 3.146589  , 3.199941  , 2.751822  ,
         2.649435  , 2.837887  , 2.836255  , 2.792137  ]),
    name = 'y',
    index = pd.date_range(start='1991-07-01', periods=204, freq='MS')
)
