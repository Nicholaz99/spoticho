#STANDARD LIBRARY FROM PYTHON
from Tkinter import *
from multiprocessing import Process
from math import log, ceil, floor
import socket
import sys
import threading
import multiprocessing
import io
import time
# 3RD LIBRARY FOR AUDIO
from pydub import AudioSegment
import pyaudio

def make_chunks(audio_segment, chunk_length):
  number_of_chunks = ceil(len(audio_segment) / float(chunk_length))
  return [audio_segment[i * chunk_length:(i + 1) * chunk_length]
    for i in range(int(number_of_chunks))]

def retrieve_song():
  sent = sock.sendto('get,', server_address)
  data, server = (sock.recvfrom(65500))
  if (data == 'end_of_song' or not data):
    return 'end'
  return data

def subscribe_server():
  global server_address
  global button_subscribe
  global is_subscribe
  global is_request
  global button_show
  global button_start
  global button_stop
  global entry_ip
  global entry_port
  global my_thread
  global is_playing
  global dd_list
  global var

  if (not is_subscribe):
    is_subscribe = True
    server_address = (entry_ip.get(), int(entry_port.get()))
    button_subscribe.configure(text='UNSUBSCRIBE')
    entry_ip.configure(state='disabled')
    entry_port.configure(state='disabled')
    button_show.configure(state='normal')
    button_start.configure(state='normal')
    button_stop.configure(state='normal')
    sent = sock.sendto('subscribe,', server_address)

  else:
    is_subscribe = False
    server_address = (entry_ip.get(), int(entry_port.get()))
    entry_ip.configure(state='normal')
    entry_port.configure(state='normal')
    button_show.configure(state='disabled')
    button_start.configure(state='disabled')
    button_stop.configure(state='disabled')
    button_subscribe.configure(text='SUBSCRIBE')
    sent = sock.sendto('unsubscribe,', server_address)
    var.set('empty')
    dd_list['menu'].delete(0, 'end')
    is_playing = False
    my_thread = None
    is_request = False
    is_subscribe = False

def show_list():
  global list_song
  global dd_list
  global var

  sent = sock.sendto('show,', server_address)
  lists, server = (sock.recvfrom(65500))
  list_song = lists.split(',')
  print list_song
  var.set('Empty')
  dd_list['menu'].delete(0, 'end')

  var.set(list_song[0])
  for song in list_song:
    dd_list['menu'].add_command(label=song, command=lambda value=song: var.set(value))
  dd_list.configure(state="normal")

def press_button_play():
  global is_playing
  global my_thread

  name = var.get()

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  if not is_playing:
    is_playing = True
    my_thread = threading.Thread(target=stream_song, args=(name,))
    my_thread.start()

def request_song(name):
  sent = sock.sendto('request,' + name, server_address)

def press_button_stop():
  global is_playing
  global my_thread
  global is_request

  if is_playing:
    is_playing = False
    my_thread.join()

def stream_song(name):
  global is_playing
  global is_request
  global current_song

  print is_request, 'wekawekaweka', name, current_song
  if (not is_request or name != current_song):
    is_request = True
    request_song(name)
    current_song = name
  p = pyaudio.PyAudio()
  data = retrieve_song()
  seg = AudioSegment.from_file(io.BytesIO(data), format="mp3")
  stream = p.open(format=p.get_format_from_width(seg.sample_width),
                  channels=seg.channels,
                  rate=seg.frame_rate,
                  output=True)
  while (data and is_playing):
    for chunk in make_chunks(seg, 65500):
      stream.write(chunk._data)
      if (not is_playing):
        break
    if (not is_playing):
      break
    data = retrieve_song()
    if (data == 'end'):
      break
    seg = AudioSegment.from_file(io.BytesIO(data), format="mp3")
  stream.stop_stream()
  stream.close()
  p.terminate()
  if (is_playing):
    is_request = False

if (__name__ == "__main__"):
  global dd_list
  global var
  global entry_ip
  global entry_port
  global button_subscribe
  global is_subscribe
  global server_address
  global button_stop
  global button_show
  global button_start
  global button_stop
  global list_song
  global current_song

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  is_playing = False
  my_thread = None
  is_request = False
  is_subscribe = False
  list_song = ["Empty"]
  current_song = ""

  root = Tk()
  root.title("Spoticho")
  root.geometry("470x200")

  #SUBSCRIBE AND UNSUBSCRIBE
  label_ip = Label(root, text="IP Server")
  entry_ip = Entry(root)
  label_port = Label(root, text="Port")
  entry_port = Entry(root)
  label_ip.grid(row=0, column=0)
  label_port.grid(row=1, column=0)
  entry_ip.grid(row=0, column=1)
  entry_port.grid(row=1, column=1)
  button_subscribe = Button(root, text="SUBSCRIBE", command=subscribe_server)
  button_subscribe.grid(row=1, column=2, sticky="ew")

  #SHOW SERVER LIST OF SONGS
  label_list = Label(root, text="List of Songs")
  button_show = Button(root, text="REFRESH LIST", command=show_list, state="disabled")
  var = StringVar(root)
  if list_song:
    var.set(list_song[0])
  dd_list = OptionMenu(root, var, *list_song)
  dd_list.configure(state="disabled")
  label_list.grid(row=2, column=0)
  dd_list.grid(row=2, column=1, sticky="ew")
  button_show.grid(row=2, column=2, sticky="ew")

  #PLAY AND PAUSE BUTTON
  button_start = Button(root, text="PLAY", command=press_button_play, state="disabled")
  button_start.grid(row=3, column=1, sticky="w", padx=(40,0))
  button_stop = Button(root, text="PAUSE", command=press_button_stop, state="disabled")
  button_stop.grid(row=3, column=1, sticky="e", padx=(0,10))

  root.mainloop()
