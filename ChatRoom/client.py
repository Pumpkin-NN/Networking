'''
Program name: ChatRoom/client.py

GUI Client: a GUI client that can communicate with the server.
            a client can send text messages to all parties in the chat room, 
            as well as receive notifications when other clients connect or disconnect. 
            Clients do not communicate directly with other clients. 
            Instead, all communication is routed through the central server.
            
Usage: Run python client.py -u <user-name> (default ip = 'localhost', default port = '8765')
'''
import socket
import threading
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.scrolledtext import ScrolledText
import argparse
import os

# Receive message from the server
def recvMessage(socket):
   while True:
      try:
         msg = socket.recv(4096).decode('utf8')
         ui_messages.insert(tk.END, f"{msg}\n")
      except OSError:
         break
      
# Send message to server
def sendMessage(flag = ""):
        if flag == "Gotta go, TTYL!":
            s.send(flag.encode('utf-8'))
            s.close()
            window.quit()
        else:
            # Get user input (minus newline character at end)
            msg = ui_input.get("0.0", tk.END+"-1c")

            print("UI: Got text: '%s'" % msg)

            s.send(msg.encode('utf-8'))
            
            if msg == "Gotta go, TTYL!":
                s.close()
                window.quit()
        
        # Add this data to the message window
        ui_messages.yview(tk.END)  # Auto-scrolling
        
        # Clean out input field for new data
        ui_input.delete("0.0", tk.END)
      
# Send file to the server
def sendFile():
   file = askopenfilename()
   if(len(file) > 0 and os.path.isfile(file)):
      print("UI: Selected file: %s" % file)
      with open(file, 'rb') as f:
         filename = b'\n<sending ' + file.split('/')[-1].encode('utf-8') + b'>... \n'
         s.send(filename + f.read())
   else:
      print("UI: File operation canceled")


# Close the window
def hover_close():
   sendMessage("Gotta go, TTYL!")

# Main funciton
if __name__ == '__main__':
    # Use argparse method
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0')
    parser.add_argument('--server_ip', '-ip', nargs='?', default='localhost')
    parser.add_argument('--server_port', '-p', nargs='?', default=8765)
    parser.add_argument('--username', '-u')
    args = parser.parse_args()
    
    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.server_ip , args.server_port))
    
    # Use tkinter
    window = tk.Tk()
    window.wm_title("ChatRoom/1.0 Connected to: "+ args.server_ip + "/"+str(args.server_port))
    window.resizable('1','1')
    
    label = tk.Label(window, text = "TYPE <Gotta go, TTYL!> to QUIT", width = 45, font=("Arial Rounded MT Bold", 12), fg="grey", anchor="w")
    label.pack()
    
    s.send(args.username.encode('utf-8'))
    
    ui_messages = ScrolledText(
            window,
            wrap=tk.WORD,
            width=50,  # In chars
            height=25)  # In chars
    ui_messages.pack(side=tk.TOP, fill=tk.BOTH)
    
    
    ui_input = tk.Text(
            window,
            wrap=tk.WORD,
            width=50,
            height=4)
    ui_input.insert(tk.END, "<Enter message>")
    ui_input.bind("<Return>", sendMessage)
    ui_input.pack(side=tk.TOP, fill=tk.BOTH)
    
    file_button = tk.Button(window, text="File", command=sendFile, width = 5)
    file_button.pack(side=tk.RIGHT)
    
    send_button = tk.Button(window, text="Send", command=sendMessage, width=5)
    send_button.pack(side=tk.LEFT)

    window.protocol("WM_DELETE_WINDOW", hover_close)

    threading.Thread(target=recvMessage, args = (s,)).start()

    tk.mainloop()


