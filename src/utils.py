import pandas as pd
import os, sys
import pathlib
from enum import Enum

def Singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@Singleton
class Utils:
    def __init__(self):
        self.base_path = self.get_base_path()
        self.music_list = self.import_music_list()
        
    @staticmethod
    def get_base_path():
        if hasattr(sys, "_MEIPASS"):
            return sys._MEIPASS
        return pathlib.Path(__file__).parent.parent.resolve()

    def resource_path(self,relative_path):
        return os.path.join(self.base_path, relative_path)

    def import_music_list(self):
        df = pd.read_excel(self.resource_path('assets/music_data/MusicData.xlsx'))
        music_list = {}

        for index, row in df.iterrows():
            music_infomation = {
                'Name': row['曲名'],
                'Composer': row['曲师'],
                'Const': row['MASTER:大师'],
                'Jacket': self.resource_path(f'assets/picture/jackets/CHU_UI_Jacket_{str(row['ID']).zfill(4)}.dds')
            }
            music_list[str(row['ID'])] = music_infomation

        df = pd.read_excel(self.resource_path('assets/music_data/MusicData_BPM_ND.xlsx'))

        for index, row in df.iterrows():
            if str(row['ID']) in music_list:
                music_list[str(row['ID'])]['BPM'] = row['BPM']
                music_list[str(row['ID'])]['ND'] = row['MASTER谱师']

        return music_list
            
class CurrentProcess(Enum):
    NONE = 0
    DISPLAY_SELECTION = 1
    RANDOM_MUSIC = 2