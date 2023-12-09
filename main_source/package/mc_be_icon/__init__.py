import zipfile,tkinter,os
icon_zip_file = zipfile.ZipFile(os.path.join("main_source","package","mc_be_icon","icon.zip"),"r")
icon_list = icon_zip_file.namelist()
icon_zip_file.extractall(os.path.join("main_source","package","mc_be_icon","icon"))

def tk_Image(name : str) :
    return os.path.join("main_source","package","mc_be_icon","icon",name)
