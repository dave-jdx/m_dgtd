import os,subprocess
# import api_model
import api_reader

def format_excange(sourceFile:str,targetFile:str):
    '''模型格式转换 使用cmd命令
    '''
    cmd_exchange = "d:/cadExchanger/bin/ExchangerConv.exe"

    cmd_exchange =cmd_exchange+ " -i " + sourceFile
    cmd_exchange =cmd_exchange+ " -e " + targetFile
    # os.system(cmd_exchange)
    # print(cmd_exchange)
    try:
        result=subprocess.check_output(cmd_exchange, shell=True, universal_newlines=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print("Command failed with return code", e.returncode)
        pass
def test():
    # fpath="D:/project/cae/emx/src/data/"
    # fname=fpath+"ffr2.txt"
    # fList=api_reader.read_ffr(fname)

    # fname=fpath+"nf.txt"
    # fList=api_reader.read_nf(fname)

    # fname=fpath+"nfr.txt"
    # fList=api_reader.read_nfr(fname)

    # format_excange("d:/model.stl","d:/model.obj")
    # print(os.path.abspath("."))
    fName="D:/project/cae/emx1.1/Ship-EMX0531V2/3.2_example1_shifeng/simple_plane.result/SBR/output/res_E_1.txt"
    fName_H="D:/project/cae/emx1.1/Ship-EMX0531V2/3.2_example1_shifeng/simple_plane.result/SBR/output/res_H_1.txt"
    fName_Power="D:/project/cae/emx1.1/Ship-EMX0531V2/3.2_example1_shifeng/simple_plane.result/SBR/output/res_Power_1.txt"
    res=api_reader.read_nf_sbr_E(fName)
    print(len(res))
    res2=api_reader.read_nf_sbr_H(fName_H)
    print("H",len(res2))
    res3=api_reader.read_nf_sbr_Power(fName_Power)
    print("Power",len(res3))
    pass
test()


