#!/usr/bin/env python3
# coding=utf-8

import argparse
import os
import shutil
import sys

import requests

SOURCE_BASE = "/data/deepin-website-services/website_source_code"
#SERVER_API_BASE = "http://10.0.1.62:8010/v1"
SERVER_API_BASE = "http://10.0.3.105:3500/v1"


def check_cl(num, clean=True):
    source_dir = os.path.join(SOURCE_BASE, num)
    exists = os.path.exists(source_dir)
    if exists and clean:
        #shutil.rmtree(source_dir)
        os.system("rm -rf %s/*" % source_dir)
    
    return exists


def sync_source(num, j_src_dir):
    source_dir = os.path.join(SOURCE_BASE, num)
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
    #ret = shutil.copytree(j_src_dir, source_dir)
    ret = os.system("cp -r %s/* %s" % (j_src_dir, source_dir))
    if ret == 0:
        return True

    return False

def get_ip_pool():
    pool = [
            "10.0.255.10",
            "10.0.255.11",
            "10.0.255.12",
            "10.0.255.13",
            "10.0.255.14",
            "10.0.255.15",
            "10.0.255.16",
            "10.0.255.17",
            "10.0.255.18",
            "10.0.255.19",
            "10.0.255.20",
            "10.0.255.21",
            "10.0.255.22",
            "10.0.255.23",
            "10.0.255.24",
            "10.0.255.25",
            "10.0.255.26",
            "10.0.255.27",
            "10.0.255.28",
            "10.0.255.29",
            ]

    return pool

def get_valid_ip():
    pool = get_ip_pool()
    ip = ""
    for _ip in pool:
        print("check ip: %s" % _ip)
        rsp = os.system("ping %s -c 1 >/dev/null" % _ip)
        print("resp: %s " % rsp)
        if rsp != 0:
            ip = _ip
            break
        else:
            print("  used, next.")

    if ip:
        return ip
    else:
        print("hell!? all of the ips in the pool are used", file=sys.stderr)
        quit(1)


def create_container(num):
    source_dir = os.path.join(SOURCE_BASE, num)
    name = "deepin-website-cl-%s" % num
    os.system("docker run --name %s --net=none -i -d -v %s:/usr/share/nginx/html nginx" % (name, source_dir))

    return name


def fix_ip(name, ip):
    ret = os.system("sudo pipework br0 %s %s/16" %(name, ip))
    if ret == 0:
        return True
    return False


def upload_result(num, ip, domain):
    #print("all of the work is finished, upload review_id and ip to server")
    #print(num, ip, domain)

    url = "%s/hosts" % SERVER_API_BASE
    d = {
        "change_number": num,
        "host": ip,
        "domain": domain
        }
    rsp = requests.post(url, data=d)
    res = rsp.json().get("result")
    if res:
        print("upload successfully~")
        print("try: http://%s" % ip)
        return True
    else:
        print("failed to upload, something wrong??")
        return False


def destroy_container(num):
    # rm the source code
    s_dir = "%s/%s" %(SOURCE_BASE, num)
    shutil.rmtree(s_dir)

    # rm container
    name = "deepin-website-cl-%s" % num
    cmd = "docker stop %s && docker rm %s" %(name, name)
    ret = os.system(cmd)
    return ret


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("change_number", help="change number")
    parser.add_argument("domain", help="website domain name of the project")
    args = parser.parse_args()
    num = args.change_number
    domain = args.domain

    cr_event_type = os.getenv("GERRIT_EVENT_TYPE")

    if cr_event_type == "change-merged":
        # destroy the container
        destroy_container(num)
        pass

    elif cr_event_type == "patchset-created":

        exists = check_cl(num)

        jenkins_src_dir = os.getenv("WORKSPACE")

        if not jenkins_src_dir:
            # tmp for test
            jenkins_src_dir = "/home/choldrim/tmp"

        jenkins_src_dir = os.path.join(jenkins_src_dir, "source")

        sync_source(num, jenkins_src_dir)

        if exists:
            print("cl (%s) exists, it won't deploy again, finish" % num)
        else:
            ip = get_valid_ip()

            name = create_container(num)

            fix_ip(name, ip)

            upload_result(num, ip, domain)
    else:
        print("E: gerrit event can't match any action")
        quit(1)


