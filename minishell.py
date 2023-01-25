#!/usr/bin/python3
import os
import shutil
import threading
from sys import stdin, stderr
from datetime import datetime
# from pwd import getpwuid

def main():
    builtins = None

    def print_flush(*args, **kwargs):
        print(*args, flush=True, **kwargs)

    def eprint(*args, **kwargs):
        print_flush(*args, file=stderr, **kwargs)

    #list the contents of a directory along with its details
    def sh_lsl(filename):
        # print("perms  num_links  owner  size  mod_time  filename")
        file_info = os.stat(os.path.join(filename))
        permissions = oct(file_info.st_mode)[-3:]
        num_links = file_info.st_nlink
        owner = file_info.st_uid
        size = file_info.st_size
        mod_time = datetime.fromtimestamp(file_info.st_mtime)
        print(f"{permissions}  {num_links}  {owner}  {size}  {mod_time}  {filename}")


    #list a directory 
    def sh_ls(args):
        if len(args)==1:
            for path in os.listdir():
                print_flush(path)
        elif len(args)==2:
            if args[1]=='-l':
                files={}
                # sh_lsl()
                for filename in os.listdir():
                    files[filename]=threading.Thread(target=sh_lsl,args=(filename,))
                    files[filename].start()
                for filename in os.listdir():
                    files[filename].join()

            elif os.path.isfile(args[1]):
                print(args[1])
            else:
                try:
                    for path in os.listdir(args[1]):
                        print_flush(path)
                except FileNotFoundError:
                    print(f"The {args[1]} does not exists. Provide a valid input!")
        else:
            eprint("Usage: {}".format(args[0]))
        
    #check current working directory
    def sh_pwd(args):
        if len(args) != 1:
            eprint("Usage: {}".format(args[0]))
        else:
            print_flush(f"Current Working Directory: {os.getcwd()}")

    #change directory
    def sh_cd(args):
        try:
            if len(args) != 2:
                eprint("Usage: {} <dir>".format(args[0]))
            else:
                os.chdir(args[1])
        except NotADirectoryError:
            print(f"{args[1]} is not a directory")
        except FileNotFoundError:
            print(f"Error: Directory {args[1]} not found")

    #display the contents of a file
    def sh_cat(args):
        try:
            if len(args) != 2:
                eprint("Usage: {} <file>".format(args[0]))
            else:
                # file=os.open(args[1],os.O_RDONLY)
                # os.system(f"cat {args[1]}")
                file=open(args[1],'r')
                print(file.read())

        except UnicodeDecodeError:
            print("*UnicodeDecodeError*")
            print("'charmap' codec can't decode byte 0x98 in position 779: character maps to <undefined>")
        except IsADirectoryError:
            print(f"{args[1]} is a directory.")
            print(f"Use ls {args[1]} to check content of a directory.")
        except FileNotFoundError:
            print(f"{args[1]} does not exists.")
            # print(f"Use ls {args[1]} to check the contents of a directory.")

    #create a file
    def sh_touch(args):
        if len(args) != 2:
            eprint("Usage: {} <file>".format(args[0]))
        else:
            open(args[1], "w").close()

    #remove a file
    def sh_rm(args):
        try:
            if len(args) != 2:
                eprint("Usage: {} <file>".format(args[0]))
            else:
                os.remove(args[1])
        except FileNotFoundError:
            print(f"{args[1]} does not exists.")
        except IsADirectoryError:
            print(f"{args[1]} is a directory.")
            print(f"Use rmdir {args[1]} to remove this directory.")

    #create a directory
    def sh_mkdir(args):
        if len(args) != 2:
            eprint("Usage: {} <dir name>".format(args[0]))
        else:
            os.mkdir(args[1])

    #remove a directory
    def sh_rmdir(args):
        try:
            if len(args) != 2:
                eprint("Usage: {} <dir name>".format(args[0]))
            else:
                os.rmdir(args[1])
        except FileNotFoundError:
            print(f"Error: Directory '{args[1]}' not found")
        except NotADirectoryError:
            print(f"Error: '{args[1]}' is not a directory")

    #move a file/directory
    def sh_mv(args):
        if len(args) != 3:
            eprint("Usage: {} <dir name> <new destination>".format(args[0]))
        else:
            shutil.copyfile(args[1],f"{args[2]}/{args[1]}")

    #copy a file/directory
    def sh_cp(args):
        try:
            if len(args) != 3:
                eprint("Usage: {} <dir name> <new destination>".format(args[0]))
            else:
                os.replace(args[1],f"{args[2]}/{args[1]}")
        except FileNotFoundError as e:
            print(f"Error:\n{e}")

    #clear the shell
    def sh_clear(args):
        if len(args) !=1:
            eprint("Usage: {}".format(args[0]))
        else:
            os.system('cls')

    #display all commands
    def sh_help(args):
        print_flush("UIT's minishell")
        print_flush("You can use the following commands in this minishell:")
        for name in builtins.keys():
            print_flush(" - {}".format(name))

    #exit the shell
    def sh_exit(args):
        exit(0)

    def launch(args):
        pid = os.fork()
        if (pid == 0):
            os.execvp(args[0], args)
        # child
        else:
        # parent
            pid, status = os.waitpid(pid, 0)

    def execute(args):
        if not args:
            return True
        # if '>'in args:
        #     print('big command')
        #     return
        if args[0] in builtins:
            return builtins[args[0]](args)
        if not (args[0].startswith('/') or args[0].startswith('.')):
            print_flush('command {} not recognized. Try \'help\''.format(args[0]))
            return
        if os.path.isfile(args[0]):
            return launch(args)



    def repl():
        user = ''
        while True:
            if not user:
                pwd = os.getcwd()
                print_flush('{}> '.format(pwd), end='')
                args = list(filter(bool, stdin.readline().strip().split()))
                execute(args)

    # optional: load .minishellrc

    builtins = {
        "ls":sh_ls, #1
        "pwd":sh_pwd, #2
        "cd":sh_cd, #3
        "help":sh_help, #4
        "exit":sh_exit, #5
        "E": sh_exit, #5
        "cat": sh_cat, #6
        "mkdir": sh_mkdir, #7
        "rmdir": sh_rmdir, #8
        "touch": sh_touch, #9
        "rm": sh_rm, #10
        "mv": sh_mv, #11
        "cp": sh_cp, #12
        "clear": sh_clear #13
    }
    repl()
    # optional: shutdown/cleanup

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n*Keyboard Interrupt*\nExiting Program!')
