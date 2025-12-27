import pandas as pd

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

    @staticmethod
    def import_music_list():
        df = pd.read_excel('assets/all_music_list.xlsx')
        music_list = {}

        for index, row in df.iterrows():
            music_infomation = {
                'Name': row['曲名'],
                'Composer': row['曲师'],
                'Const': row['MASTER:大师'],
                'Jacket': f'assets/picture/jackets/CHU_UI_Jacket_{str(row['ID']).zfill(4)}.dds'
            }
            music_list[str(row['ID'])] = music_infomation

        return music_list