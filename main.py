from tkinter import*
root = Tk()
root.geometry("900x700")
root.title("Tic-Tac Games Player")
root.config(bg='#0B074F')
photo = PhotoImage(file="logo.png")
afflogo = Label(root, image=photo)
afflogo.pack()
root.mainloop()
