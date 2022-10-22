def exec(cmd):
    import subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return (out, err)
