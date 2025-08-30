import os
import hashlib
import uuid
import subprocess
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64
from PyQt5.QtCore import QSettings, QStandardPaths
password = "CsicShipEmx23061"
default_license_file=QStandardPaths.writableLocation(QStandardPaths.GenericConfigLocation)+"/ShipEMX/license/shipemx.lic"
    
def get_hardId():
    '''
    获取硬件ID
    '''
    mac_address = get_mac_address()
    disk_serial_number = get_disk_serial_number()

    unique_value = mac_address + disk_serial_number
    md5_value = generate_md5(unique_value)
    return md5_value
    pass

def validate_license(licenseCode:str):
    '''验证license是否通过
    '''
    try:
        decrypted_text = decrypt(licenseCode, produce_key(password))

        arr=decrypted_text.split(",")
        
        hardId=arr[0]
        vDate=arr[1]
        # print("license",hardId,vDate)
        if(hardId==get_hardId()):
            return (1,"success")
        return(-1,"license is not validated.")
    except Exception as e:
        return(-2,"license error:"+str(e))
        pass
    pass
def produce_license(hardId:str):
    '''生成license
    key:hardId,expiredDate
    '''
    plain_text=hardId+",2099-12-31"
    encrypted_text=encrypt(plain_text,produce_key(password))
    return encrypted_text
    pass
def get_mac_address():
    mac_address = uuid.getnode()
    mac_address = ':'.join(("%012X" % mac_address)[i:i+2] for i in range(0, 12, 2))
    return mac_address
def get_disk_serial_number():
    output = subprocess.check_output('wmic diskdrive get serialnumber',creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
    lines = output.split('\n')
    serial_number = lines[1].strip()
    return serial_number
def generate_md5(value):
    md5_hash = hashlib.md5()
    md5_hash.update(value.encode('utf-8'))
    md5_value = md5_hash.hexdigest()
    return md5_value
def encrypt(plaintext, key):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))
    encoded_ciphertext = base64.b64encode(iv + ciphertext).decode()
    return encoded_ciphertext

def decrypt(ciphertext, key):
    decoded_ciphertext = base64.b64decode(ciphertext)
    iv = decoded_ciphertext[:AES.block_size]
    ciphertext = decoded_ciphertext[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    plaintext = decrypted_data.decode("utf-8")
    return plaintext
def produce_key(password:str):
    # 使用PBKDF2生成密钥
    password=generate_md5(password+"csixemx0981")
    salt = b'Emx101' # 盐值（随机的唯一字符串）
    key = PBKDF2(password, salt, dkLen=16)  # 生成16字节密钥
    return key
def license_validated():
    '''
    判断license是否通过验证
    '''
    fname=default_license_file
    if(os.path.exists(fname)):
        licenseCode=readLicenseCode(fname)
        if(licenseCode==""):
            return ("-1","license code is empty.")
        return validate_license(licenseCode)
    return ("-2","license file is not exist.")
    pass
def register(licenseCode:str):
    '''
    将licenseCode写入到license文件中
    '''
    fname=default_license_file
    try:
        fpath=os.path.dirname(fname)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        with open(fname,"w") as f:
            f.write(licenseCode)
            return (1,"success")
    except Exception as e:
        # print("register error:",e)
        return (-1,"register error:"+str(e))
    
    pass
def readLicenseCode(fname:str):
    '''
    读取license文件，根据传入的文件名读取文件内容，并返回字符串
    ''' 
    try:
        with open(fname,"r") as f:
            str= f.read()
            return str
    except Exception as e:
        return ""
        pass

    pass
# hardId=get_hardId()
# hardId='7a8f8bba9eb99d1fe3531fd323e7d00f'
# licensecode=produce_license(hardId)
# print("licensecode",licensecode)
# print("decrypt",licensecode,validate_license(licensecode))
