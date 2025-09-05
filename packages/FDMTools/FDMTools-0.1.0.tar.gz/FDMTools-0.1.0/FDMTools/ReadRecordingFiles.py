import os
import time
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from decimal import Decimal

from neo.core import AnalogSignal, Block, Segment, Event
from neo.io import NixIO
import quantities as pq
import numpy as np

from FDMTools.LoadConditions import ReadGuiConfFile, CreateLockIns

# TODO Validate this
Bits = 13
FullRangeCenter = int(2 ** Bits / 2)


def ReadNpyList(FileIn):
    f = open(FileIn, 'rb')
    OutList = []
    while True:
        try:
            b = np.load(f)
            OutList.append(b)
        except:
            break
    f.close()
    return OutList


def ReadNpy(FileIn):
    OutList = ReadNpyList(FileIn)
    Buffer = np.zeros((OutList[0].shape[0] * len(OutList), OutList[0].shape[1]),
                      dtype=OutList[0].dtype)
    index1 = 0
    for ic, d in enumerate(OutList):
        index2 = index1 + d.shape[0]
        Buffer[index1:index2, :] = d
        index1 = index2
    return Buffer


def Checker(Buffer):
    if all(Buffer[:, 0] >= 40960):
        Buffer_Column = Buffer[:, 0] & 0x001f  # 5'b1 Column counter
        Pointers = np.where(np.diff(np.where(np.diff(Buffer_Column) != 1)[0]) != 32)[0]
        if len(Pointers) > 0:
            print("ERROR on received Columns")
            return True
    else:
        print("Error on received Header")
        return True
    return False


def ReadRecordFile(RecFile):
    Data = ReadNpy(RecFile)
    if Checker(Data):
        print("ERROR on received Data")
        return None
    TTL = (Data[:, 0] & 0x00e0) >> 5
    return Data[:, 1:], TTL


def DemuxRecordFile(RecFile, LockIns, DownFactor, dtype=np.complex64, DataOffset=None, LSB=1):
    if DataOffset is None:
        DataOffset = FullRangeCenter

    executor = ThreadPoolExecutor(max_workers=16)
    OutList = ReadNpyList(RecFile)

    nSamples = int(OutList[0].shape[0] * len(OutList) / DownFactor)
    Data = np.zeros((nSamples, len(LockIns)), dtype=dtype)
    TTL = np.zeros(nSamples, dtype=np.int8)
    index1 = 0
    for Chunk in OutList:
        if Checker(Chunk):
            print("ERROR on received Data")

        ttl = (Chunk[:, 0] & 0x00e0) >> 5
        Chunk -= DataOffset  # TODO Check Bits Scaling

        futures = []
        for LockIn in LockIns.values():
            futures.append(executor.submit(LockIn.CalcData, Chunk))

        index2 = index1 + int(OutList[0].shape[0] / DownFactor)
        for res in futures:
            d, chIndex, (TIAGain, RowGain) = res.result()
            # TODO Check Bits Scaling and Current Conversion
            dV = d * LSB  # Conversion to Volts
            dI = (dV / RowGain) / TIAGain  # Conversion to Ids Current
            Data[index1:index2, chIndex] = dI

        TTL[index1:index2] = ttl[::DownFactor]
        index1 = index2

    return Data, TTL


def SaveAsNeo(FileOut, FullRec, TTL, Annotations, sKwargs, OverWrite=True):
    Sigs = AnalogSignal(FullRec * pq.A,
                        name='Demuxed',
                        **sKwargs)
    Sigs.annotate(**Annotations)

    sTTL = AnalogSignal(TTL * pq.dimensionless,
                        name='TTL',
                        **sKwargs)

    SegData = Segment()
    SegData.analogsignals.append(Sigs)

    SegTTL = Segment()
    SegTTL.analogsignals.append(sTTL)

    Blk = Block()
    Blk.segments.append(SegData)
    Blk.segments.append(SegTTL)

    if os.path.isfile(FileOut):
        if OverWrite:
            os.remove(FileOut)
            print('File removed ', FileOut)
        else:
            print('Warning File Exsist')

    Outf = NixIO(FileOut)
    Outf.write(Blk)
    Outf.close()


class RecReader:
    Bits = 13
    FullRangeCenter = int(2 ** Bits / 2)
    VFS = 2.0
    LSB = VFS / (2 ** Bits)

    def __init__(self, FileConf, OutFile=None, DownFactor=100):
        self.VgsExp = None
        self.BufferSampleSize = None
        self.FsOut = None
        self.FsIn = None
        self.AcqConf = None
        self.ReadBlocks = None
        self.DictFiles = None
        self.RecFiles = None
        self.FileConf = FileConf
        self.DownFactor = int(DownFactor)
        self.Outfile = OutFile

        self.ReadConfFile()
        self.GetRecFiles()
        self.IndexFiles()

    def ReadConfFile(self, FileConf=None):
        if FileConf is not None:
            self.FileConf = FileConf
        self.AcqConf = ReadGuiConfFile(self.FileConf)
        self.FsIn = self.AcqConf['Fs']
        self.FsOut = self.FsIn / self.DownFactor
        self.BufferSampleSize = self.AcqConf['BufferSampleSize']
        self.VgsExp = self.AcqConf['VgsExp']

    def GetRecFiles(self):
        RecFilesFilter = self.FileConf.replace('.pkl', '*.npy')
        self.RecFiles = glob(RecFilesFilter)
        self.RecFiles.sort(key=lambda x: os.path.getmtime(x))

    def IndexFiles(self, FileConf=None):
        if FileConf is not None:
            self.FileConf = FileConf
            self.GetRecFiles()

        self.DictFiles = {}
        t_start = 0
        for ic, RecFile in enumerate(self.RecFiles):
            dataList = ReadNpyList(RecFile)
            nSamples = len(dataList) * self.BufferSampleSize
            t_end = t_start + nSamples / self.FsIn

            self.DictFiles[RecFile] = {'nFile': ic,
                                       'nSamples': nSamples,
                                       't_start': t_start,
                                       't_end': t_end, }
            t_start = t_end


    def CalcReadBlocks(self, BlockTime=200, BlStart=None, BlStop=None):
        self.ReadBlocks = []
        bl = []
        Block_t_start = 0
        for RecFile, fTimes in self.DictFiles.items():
            if BlStart is not None:
                if fTimes['t_start'] < BlStart:
                    Block_t_start = fTimes['t_end']
                    continue
            if BlStop is not None:
                if fTimes['t_end'] > BlStop:
                    break
            bl.append(RecFile)
            if fTimes['t_end'] - Block_t_start > BlockTime:
                Block_t_start = fTimes['t_end']
                self.ReadBlocks.append(self.GenBlockTimes(bl))
                bl = []
        if len(bl) > 0:
            self.ReadBlocks.append(self.GenBlockTimes(bl))

    def GenBlockTimes(self, bl):
        nSamples = 0
        for recfile in bl:
            nSamples += self.DictFiles[recfile]['nSamples']

        return {'BlockFiles': bl,
                'T_start': self.DictFiles[bl[0]]['t_start'],
                'T_end': self.DictFiles[bl[-1]]['t_end'],
                'Duration': self.DictFiles[bl[-1]]['t_end'] - self.DictFiles[bl[0]]['t_start'],
                'nSamples': nSamples,
                }

    def GenNeoFiles(self, BlockTime=200, BlStart=None, BlStop=None, OverWrite=True, OutFile=None, DownFactor=100):
        if OutFile is not None:
            self.Outfile = OutFile
        if self.Outfile is None:
            print('Output file not defined')
            return
        if DownFactor is not None:
            self.DownFactor = DownFactor
        if self.DownFactor is None:
            print('DownFactor not defined')
            return

        # CalcReadBlocks
        self.CalcReadBlocks(BlockTime, BlStart, BlStop)
        # CreateLockIns
        LockIns, LockInsConf = CreateLockIns(self.AcqConf, self.DownFactor)

        # Define annotations for neo signals
        ChSorting = []
        ChDescription = []
        for chName, lock in LockIns.items():
            ChSorting.append(lock.Index)
            ChDescription.append(chName)
        Annotations = {'ChSorting': ChSorting,
                       'ChDescription': ChDescription,
                       'VgsExp': - self.VgsExp}

        # Iterate over blocks
        for ic, Bl in enumerate(self.ReadBlocks):
            print('Block', ic, Bl['T_start'], Bl['T_end'], Bl['Duration'], Bl['nSamples'])
            RecFiles = Bl['BlockFiles']
            nSamples = Bl['nSamples']/self.DownFactor
            if Decimal(nSamples).as_integer_ratio()[1] > 1:
                print("ERROR nSamples", nSamples, Decimal(nSamples).as_integer_ratio())
                return
            else:
                nSamples = int(nSamples)
            # Dimensioning full recording array
            FullRec = np.zeros((nSamples, len(LockIns)), dtype=np.complex64)
            FullTTL = np.zeros(nSamples, dtype=np.int8)
            Index1 = 0
            # Iterate over recordings in block
            for ir, RecFile in enumerate(RecFiles):
                print('{}/{} -- {}'.format(ir, len(RecFiles), RecFile))
                Time_act = time.time()  # Debug timer

                Data, TTL = DemuxRecordFile(RecFile=RecFile,
                                            LockIns=LockIns,
                                            DownFactor=self.DownFactor,
                                            dtype=np.complex64,
                                            DataOffset=self.FullRangeCenter,
                                            LSB=self.LSB)
                if self.DictFiles[RecFile]['nSamples']/self.DownFactor != Data.shape[0]:
                    print("ERROR Data shaping", self.DictFiles[RecFile]['nSamples']/self.DownFactor, Data.shape[0])
                Index2 = Index1 + Data.shape[0]
                FullRec[Index1:Index2, :] = Data
                FullTTL[Index1:Index2] = TTL
                Index1 = Index2

                print("Time", time.time() - Time_act)  # Debug timer

            sKwargs = {'sampling_rate': self.FsOut * pq.Hz,
                       't_start': Bl['T_start'] * pq.s,
                       'file_origin': RecFiles[0]}

            FileOut = self.Outfile.replace('.h5', '_{:03d}.h5'.format(ic))
            SaveAsNeo(FileOut, FullRec, FullTTL, Annotations, sKwargs, OverWrite)
