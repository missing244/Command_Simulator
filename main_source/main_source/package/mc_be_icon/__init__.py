import zipfile,tkinter,os
now_dir = os.path.realpath(os.path.join(__file__, os.pardir))

icon_zip_file = zipfile.ZipFile(os.path.join(now_dir,"icon.zip"),"r")
icon_list = icon_zip_file.namelist()
icon_zip_file.extractall(os.path.join(now_dir,"icon"))

def tk_Image(name : str) :
    return tkinter.PhotoImage(file=os.path.join(now_dir,"icon",name))
