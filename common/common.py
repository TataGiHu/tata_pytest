# !/usr/bin/python
# -*- coding: UTF-8 -*-
# README:
#       It provides the general interface functions required
#   to build customized common functios. You can build your
#   own common functions based on these functions.


from modulefinder import packagePathMap
from struct import pack
import pytest
import paramiko
import time
import os
import yaml
import sys
from stat import S_ISDIR as isdir



#############################################
#                                           #
#       General Interface Functions         #
#                                           #
#   Note: Here are the general interface    # 
#         functions requied to build your   #
#         own common fucntion.              #                      
#                                           #
#############################################
# define the system time getting function
def getTime():
    cur = time.localtime()
    cur_time = time.strftime("%Y%m%d",cur)
    return cur_time

# define the config reading function
def readConfig():
    file_path = os.path.abspath(__file__)
    test_path = os.path.dirname(os.path.dirname(file_path))
    yamlPath = os.path.join(test_path+"/config/", "config.yml")
    f = open(yamlPath, 'r', encoding='utf-8')
    cfg = f.read()
    params = yaml.load(cfg, Loader=yaml.SafeLoader)
    return test_path,params

# connection establishing function
def sftpConnect(host, user, password, port):
    client = None
    sftp = None
    try:
        client = paramiko.Transport((host, port))
        print("Client: Generate Success")
    except Exception as error:
        print(error)
    else:
        try:
            client.connect(username=user, password=password)
        except Exception as error:
            print(error)
        else:
            sftp = paramiko.SFTPClient.from_transport(client)
            print("SFTP: Generate Success")
    return client,sftp

# connection breaking function
def sftpDisconnect(client):
    try:
        client.close()
        print("SFTP: Disconnected")
    except Exception as error:
        print(error)

# local directory checking function
def checkLocal(local):
    if not os.path.exists(local):
        try:
            os.mkdir(local)
        except IOError as err:
            print(err)

# downloading fucntion
def sftpDownload(sftp, remote, local):
    # check remote directory's existence
    try:
        result = sftp.stat(remote)
    except IOError as err:
        error = '[ERROR %s] %s %s' %(err.errno,os.path.basename(os.path.normpath(remote)),err.strerror)
        print(error)
    else:
        # check remote file is directory or not
        if isdir(result.st_mode):
            dirname = os.path.basename(os.path.normpath(remote))
            local = os.path.join(local, dirname)
            checkLocal(local)
            for file in sftp.listdir(remote):
                sub_remote = os.path.join(remote, file)
                sftpDownload(sftp, sub_remote, local)
        # copy files
        else:
            if os.path.isdir(local):
                local = os.path.join(local, os.path.basename(remote))
            try:
                sftp.get(remote, local)
            except IOError as err:
                print(err)
            else:
                print ("[get]",local,"<==",remote)

# uploading function
def sftpUpload(sftp, local, remote):
    # check directory's existence
    def _is_exists(path, function):
        try:
            function(path)
        except Exception as error:
            return False
        else:
            return True
    # copy files
    def _copy(sftp, local, remote):
        if _is_exists(remote, function=sftp.chdir):
            filename = os.path.basename(os.path.normpath(local))
            remote = os.path.join(remote, filename)
        if os.path.isdir(local):
            _is_exists(remote, function=sftp.mkdir)
            for file in os.listdir(local):
                localfile = os.path.join(local, file)
                _copy(sftp=sftp, local=localfile, remote=remote)
        if os.path.isfile(local):
            try:
                sftp.put(local, remote)
            except Exception as error:
                print(error)
                print("[put]",local,"==>",remote,"Failed")
            else:
                print("[put]",local,"==>",remote,"Successed")
    if not _is_exists(local, function=os.stat):
        print("'"+local+"': No such file or directory in local")
        return False
    remote_parent = os.path.dirname(os.path.normpath(remote))
    if not _is_exists(remote_parent, function=sftp.chdir):
        print("'"+remote+"': No such file or directory in remote")
        return False
    _copy(sftp=sftp, local=local, remote=remote)

# Allure deployment function
def allureDeploy():
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cmd = "export PATH=" + test_path + "/allure2/bin:$PATH;\
        export JAVA_HOME=" + test_path + "/jdk-18.0.1.1;\
        export CLASSPATH=$JAVA_HOME/lib:$CLASSPATH;\
        export PATH=$JAVA_HOME/bin:$PATH;\
        allure generate " + test_path + "/temp -o " + test_path + "/allure_report --clean"
    os.system(cmd)




####################################################
# Some common functions for 8 examples' daily test #
####################################################
# define the package download function
def downloadPackage():
    test_path, params = readConfig()
    if (params['TIME'] != None):
        cur_time = str(params['TIME'])
    else:
        cur_time = getTime()
    print("Current test version: {}".format(cur_time))
    ftp_config = params['FTP']
    ftp_ip = ftp_config['FTP_IP']
    ftp_user = ftp_config['FTP_USER']
    ftp_pwd = ftp_config['FTP_PWD']
    # test package download
    cmd = "mkdir " + test_path + "/test_package;cd " + test_path + "/test_package;\
        wget -np ftp://"+ ftp_ip +":/all_in_one/daily_build/Master_" + cur_time + "* \
            --ftp-user=" + ftp_user + " --ftp-password=" + ftp_pwd + " -r;cd "+ test_path + \
                "/test_package/" + ftp_ip + "/all_in_one/daily_build;mv -f Master_" + cur_time + "* ../../../;cd ../../../;\
                    rm -rf "+ftp_ip
    print("cmd: {}".format(cmd))
    os.system(cmd)


# define the MD5 checking function
def checkMD5():
    test_path, params = readConfig()
    if (params['TIME'] != None):
        cur_time = str(params['TIME'])
    else:
        cur_time = getTime()
    print("Note: MD5 Checking...")
    package_path = os.path.abspath(test_path+"/test_package/Master_"+cur_time+"*")
    cmd = "md5sum " + package_path+ "/iso/system.tgz " + \
        package_path + "/sophonsdk/sophonsdk_vMaster.tar.gz " + \
            package_path + "/test/x86_pcie_test.tar > "+ test_path +"/log/"+cur_time+"_MD5.log"
    os.system(cmd)


# define the scp function
def fileUpload(mode):
    test_path, params = readConfig()
    video264_path = os.path.dirname(test_path)+"/stream/a.264"
    videomp4_path = os.path.dirname(test_path)+"/stream/opencv_input.mp4"
    figure_path = os.path.dirname(test_path)+"/stream/opencv_nv12_4k_test.jpg"
    os.chdir(os.path.dirname(video264_path))
    os.system("chmod 777 a.264")
    os.system("chmod 777 opencv_input.mp4")
    cur_time = str(params['TIME'])
    config = params[mode]
    ip = config[mode+"_IP"]
    user = config[mode+"_USER"]
    pwd = config[mode+"_PWD"]
    port = config[mode+"_PORT"]
    remote_path = config[mode+'_PATH']
    file_list = os.listdir(test_path + "/test_package")
    for file in file_list:
        if cur_time in file:
            file_name = file
    package_path = test_path + "/test_package/" + file_name
    client,sftp = sftpConnect(ip, user, pwd, port)
    print("Note: test files uploading...")
    if mode == "SOC":
        soc_package_path = package_path + "/iso/system.tgz"
        sftpUpload(sftp, soc_package_path, remote_path)
        sftpUpload(sftp, video264_path, remote_path)
        sftpUpload(sftp, videomp4_path, remote_path)
        sftpUpload(sftp, figure_path, remote_path)
    elif mode == "PCIE":
        pcie_test_path = package_path + "/test/x86_pcie_test.tar"
        pcie_sdk_path = package_path + "/sophonsdk/sophonsdk_vMaster.tar.gz"
        sftpUpload(sftp, pcie_test_path, remote_path)
        sftpUpload(sftp, pcie_sdk_path, remote_path)
        sftpUpload(sftp, video264_path, remote_path)
        sftpUpload(sftp, videomp4_path, remote_path)
        sftpUpload(sftp, figure_path, remote_path)
    else:
        print("Error: mode selection wrong(Only SOC/PCIE is acceptable)")
        return False
    sftpDisconnect(client)   


# define the package unzip function
def unzipPackage(mode):
    file_path = os.path.abspath(__file__)
    test_path = os.path.dirname(os.path.dirname(file_path))
    yamlPath = os.path.join(test_path+"/config/", "config.yml")
    f = open(yamlPath, 'r', encoding='utf-8')
    cfg = f.read()
    params = yaml.load(cfg, Loader=yaml.SafeLoader)
    config = params[mode]
    ip = config[mode+"_IP"]
    user = config[mode+"_USER"]
    pwd = config[mode+"_PWD"]
    port = config[mode+"_PORT"]
    remote_path = config[mode+"_PATH"]
    if mode == "SOC":
        cmd = "cd " + remote_path + ";sudo tar -zxvf system.tgz;mkdir pytest_daily;\
            mv -f a.264 pytest_daily;mv -f opencv_nv12_4k_test.jpg pytest_daily;mv -f opencv_input.mp4 pytest_daily"
    elif mode == "PCIE":
        cmd = "cd "+ remote_path + ";mkdir pytest_daily;mv -f a.264 pytest_daily;\
            mv -f opencv_input.mp4 pytest_daily;mv -f opencv_nv12_4k_test.jpg pytest_daily;\
            mv -f x86_pcie_test.tar pytest_daily;mv -f sophonsdk_vMaster.tar.gz pytest_daily;\
                cd pytest_daily;tar -zxvf sophonsdk_vMaster.tar.gz;\
                    tar -zxvf x86_pcie_test.tar"
    else:
        print("Error: mode selection wrong(Only SOC/PCIE is acceptable)")
        return False
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,port,user,pwd)
    print("Note: Test package unzipping...")
    _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in stdout.readlines():
        print(line.strip())
    for line in stderr.readlines():
        print(line.strip())
    ssh.close()

# define the temp files cleaning function
def cleanTemp():
    file_path = os.path.abspath(__file__)
    test_path = os.path.dirname(os.path.dirname(file_path))
    cmd = "cd " + test_path + "/temp;rm -rf *"
    os.system(cmd)    


