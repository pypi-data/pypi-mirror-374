import os

def rfile(name):
  with open(name, "r") as f:
    print(f.read())

def cfile(name):
  open(name, "x")

def wfile(name, text):
  with open(name, "a") as f:
    f.write("\n" + text)

def dfile(name):
  os.remove(name)

#file manager