import pickle
from FDMTools.Lockin import LockIn


def GetDict(cDict):
    ret = {}
    for k, v in cDict.items():
        ret[k] = v['value']
    return ret


def ReadGuiConfFile(FileConf):
    ConfDict = pickle.load(open(FileConf, 'rb'), encoding='latin1')

    RowsDic = ConfDict['ASICConf']['children']['RowsConf']['children']['Rows']['children']
    ColsDic = ConfDict['ASICConf']['children']['ColsConf']['children']['Cols']['children']
    Fs = ConfDict['LockInConf']['children']['InputSetting']['children']['Fs']['value']
    BufferSampleSize = ConfDict['LockInConf']['children']['InputSetting']['children']['BufferSampleSize']['value']
    VgsExp = ConfDict['ASICConf']['children']['DACsConf']['children']['G']['children']['Value']['value']

    Rows = {}
    for Row, d in RowsDic.items():
        rconf = d['children']
        if rconf['Enable']['value']:
            Rows[Row] = GetDict(rconf)

    Cols = {}
    for Col, d in ColsDic.items():
        cconf = d['children']
        if cconf['Enable']['value']:
            Cols[Col] = GetDict(cconf)

    AcqConf = {'Cols': Cols,
               'Rows': Rows,
               'Fs': Fs,
               'VgsExp': VgsExp,
               'BufferSampleSize': BufferSampleSize}

    return AcqConf


def CreateLockIns(AcqConf, DownFactor=100):
    FsOut = AcqConf['Fs'] / DownFactor
    Filter = {'N': 8,
              'Wn': (FsOut / 2,),
              'btype': 'lowpass',
              'fs': AcqConf['Fs'], }

    LockInsConf = {}
    index = 0
    for Row, Rconf in AcqConf['Rows'].items():
        for Col, Cconf in AcqConf['Cols'].items():
            if Cconf['Freq'] > 300e3:
                continue

            LockInsConf[Row + Col] = {'FsIn': AcqConf['Fs'],
                                      'Fc': Cconf['Freq'],
                                      'Filter': Filter,
                                      'BufferSize': AcqConf['BufferSampleSize'],
                                      'DownFactor': DownFactor,
                                      'nRow': Rconf['Index'],  # Index of the row in input buffer
                                      'Index': index,  # Index of the output for output stacking
                                      'RowGain': Rconf['Gain'],  # Row gain
                                      'TIAGain': 5e3,  # TIA gain
                                      }
            index += 1
    LockIns = {}
    for ChName, LConf in LockInsConf.items():
        LockIns[ChName] = LockIn(**LConf)

    return LockIns, LockInsConf
