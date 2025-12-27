import pandas as pd
import os
import pathlib

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
        self.music_list = self.import_music_list()
        self.project_root = self.get_project_root()

    @staticmethod
    def import_music_list():
        df = pd.read_excel('assets/music_data/MusicData.xlsx')
        music_list = {}

        for index, row in df.iterrows():
            music_infomation = {
                'Name': row['曲名'],
                'Composer': row['曲师'],
                'Const': row['MASTER:大师'],
                'Jacket': f'assets/picture/jackets/CHU_UI_Jacket_{str(row['ID']).zfill(4)}.dds'
            }
            music_list[str(row['ID'])] = music_infomation

        df = pd.read_excel('assets/music_data/MusicData_BPM_ND.xlsx')

        for index, row in df.iterrows():
            if str(row['ID']) in music_list:
                music_list[str(row['ID'])]['BPM'] = row['BPM']
                music_list[str(row['ID'])]['ND'] = row['MASTER谱师']

        return music_list

    @staticmethod
    def get_project_root():
        current_path = pathlib.Path(__file__).resolve()
        for parent in current_path.parents:
            if (parent / 'src').exists():
                return parent