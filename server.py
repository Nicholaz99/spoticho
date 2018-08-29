from Tkinter import *
import socket
import sys
import os
import time
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
list_song = {}
list_file = ["Empty"]
list_ava_music = ["Empty"]
list_client = {}

def onClose():
  exit()

def show_list_song():
  data = []
  for key in list_ava_music:
    data.append(key)
  return ",".join(data)

def refresh_list():
  files = os.listdir(os.curdir+'/music')
  for file in files:
    if (not file in list_file):
      list_file.append(file)
  var.set('Empty')
  dd_list['menu'].delete(0, 'end')

  var.set(list_file[len(list_file)-1])
  for song in list_file:
    dd_list['menu'].add_command(label=song, command=lambda value=song: var.set(value))
  dd_list.configure(state="normal")

def load_songs():
  files = os.listdir(os.curdir+'/music')
  for file in files:
    list_file.append(file)

def add_music():
  global dd_list
  global var
  global var2

  file = var.get()
  print file
  list_song[file] = []
  with open('music/'+file, 'rb') as infile:
    d = infile.read(65500)
    while d :
      list_song[file].append(d)
      d = infile.read(65500)
    list_song[file].append('end_of_song')
  list_ava_music.append(file)
  var2.set('Empty')
  dd_list2['menu'].delete(0, 'end')

  var2.set(list_ava_music[len(list_ava_music)-1])
  for song in list_ava_music:
    dd_list2['menu'].add_command(label=song, command=lambda value=song: var2.set(value))
  dd_list2.configure(state="normal")

def delete_music():
  file = var2.get()
  list_ava_music.remove(file)
  var2.set('Empty')
  dd_list2['menu'].delete(0, 'end')

  var2.set(list_ava_music[len(list_ava_music)-1])
  for song in list_ava_music:
    dd_list2['menu'].add_command(label=song, command=lambda value=song: var2.set(value))
  dd_list2.configure(state="normal")

def handle_receive():
  while 1:
    print >> sys.stderr, '\nWaiting to receive message...'
    data, address = sock.recvfrom(1024)
    raw_data = data.split(',')
    if (raw_data[0] == 'subscribe'):
      list_client[address] = {}
      print list_client
      print >> sys.stderr, address, 'Subscribed to this server!!'
    elif (raw_data[0] == 'unsubscribe'):
      list_client.pop(address, None)
      print list_client
    elif (raw_data[0] == 'get'):
      name = list_client[address]['current_song']
      pos = list_client[address]['current_position']
      sock.sendto(list_song[name][pos], address)
      list_client[address]['current_position'] += 1
      if (pos + 1 == len(list_song[name])):
        list_client[address] = {}
    elif (raw_data[0] == 'show'):
      songs = show_list_song()
      sock.sendto(songs, address)
    elif (raw_data[0] == 'request'):
      print raw_data
      if (raw_data[1] in list_song):
        list_client[address]['current_song'] = raw_data[1]
        list_client[address]['current_position'] = 0

if (__name__ == "__main__"):
  global var
  global var2
  server_address = ('localhost', 10000)
  print >> sys.stderr, 'Starting up on %s port %s' % server_address
  sock.bind(server_address)
  load_songs()
  my_thread = threading.Thread(target=handle_receive)
  my_thread.start()

  root = Tk()
  root.title("Spoticho Server")
  root.geometry("550x200")

  label_list = Label(root, text="List of Music File")
  label_list_song = Label(root, text="Current List")
  button_add = Button(root, text="Add Song", command=add_music)
  button_delete = Button(root, text="Delete Song", command=delete_music)
  button_refresh = Button(root, text="Refresh List File", command=refresh_list)
  var = StringVar(root)
  var2 = StringVar(root)
  if list_file:
    var.set(list_file[0])
  if list_ava_music:
    var2.set(list_ava_music[0])
  dd_list = OptionMenu(root, var, *list_file)
  dd_list2 = OptionMenu(root, var2, *list_ava_music)

  label_list.grid(row=2, column=0)
  label_list_song.grid(row=3, column=0)
  dd_list.grid(row=2, column=1, sticky="ew")
  dd_list2.grid(row=3, column=1, sticky="ew")
  button_add.grid(row=2, column=3, sticky="ew")
  button_delete.grid(row=3, column=3, sticky="ew")
  button_refresh.grid(row=2, column=4, sticky="ew")
  root.mainloop()
