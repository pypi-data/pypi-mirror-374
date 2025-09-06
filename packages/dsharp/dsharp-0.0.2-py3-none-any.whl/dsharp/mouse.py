import pyautogui

def mousemove(x, y):
  pyautogui.moveTo(x, y)

def mouseclick(x, y):
  pyautogui.click(x, y)

def mousedrag(x, y):
  pyautogui.dragTo(x, y)

def keypress(key):
  pyautogui.press(key)

def onpress(key):
  pyautogui.keyDown(key)

def offpress(key):
  pyautogui.keyUp(key)

