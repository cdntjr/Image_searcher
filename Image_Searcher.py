from tkinter import *
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.messagebox as msgbox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import webbrowser
import urllib
import time
import os

from io import BytesIO
import win32clipboard
from PIL import Image




root = Tk()
root.title("Image Searcher")
root.geometry("740x680")

root.resizable(False, False)



def option_reset():

    find_CD.chromedriver_path_ent.configure(state="normal")
    find_CD.chromedriver_path_ent.delete(0, END)
    find_CD.chromedriver_find_btn_askdir.configure(state="normal")

    all_disable()




def link_chromedriver():
    webbrowser.open("https://chromedriver.chromium.org/downloads")




def add_chromedriver_path():
    files = filedialog.askopenfilenames(title="파일 선택", \
        filetypes=(("모든 파일", "*.*"), ("EXE", "*.exe")), initialdir="C:/") 

    for file in files:
        find_CD.chromedriver_path_ent.delete(0, END)
        find_CD.chromedriver_path_ent.insert(END, file)

    all_enable()




def add_image_path():

    files = filedialog.askopenfilenames(title="파일 선택", \
        filetypes=(("모든 파일", "*.*"), ("JPG", "*.jpg"), ("PNG", "*.png")), initialdir="C:/") 
  
    for file in files:
        similar.image_path_ent.delete(0, END)
        similar.image_path_ent.insert(END, file)

    keyword_image_search_disable()




def similar_add_path():
    global folder_selected

    folder_selected = filedialog.askdirectory(title="폴더 선택", initialdir="C:/")

    if folder_selected is None:
        return
    

    similar.file_path_ent.delete(0, END)
    similar.file_path_ent.insert(0, folder_selected)

    keyword_image_search_disable()




def keyword_add_path():
    global folder_selected

    folder_selected = filedialog.askdirectory(title="폴더 선택", initialdir="C:/")

    if folder_selected is None:
        return
    

    keyword.file_path_ent.delete(0, END)
    keyword.file_path_ent.insert(0, folder_selected)

    similar_image_search_disable()




def start_search():

    if os.path.isfile(find_CD.chromedriver_path_ent.get()) == True and os.path.basename(find_CD.chromedriver_path_ent.get()) == "chromedriver.exe":

        if similar.image_path_ent.get() != '' or similar.file_path_ent.get() != '' or similar.count_ComboBox.get() != 'Image Count':
            similar_Image_Scraping()

        elif keyword.file_path_ent.get() != '' or keyword.image_keyword_ent.get() != '' or keyword.count_ComboBox.get() != 'Image Count' or keyword.background_chkvar.get() != 1:
            Keyword_image_scraping()

        else:
            msgbox.showwarning("Warning", "입력한 값을 다시 확인해 주세요.")

    else:
        msgbox.showwarning("Warning", "Chrome driver을 찾지 못했습니다.")




def similar_Image_Scraping():

    def send_to_clipboard(clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()

    filepath = similar.image_path_ent.get()
    image = Image.open(filepath)

    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    send_to_clipboard(win32clipboard.CF_DIB, data)


    driver = webdriver.Chrome(find_CD.chromedriver_path_ent.get())
    driver.set_window_size(800, 750)

    driver.get("https://yandex.com/images/?utm_source=yandex&utm_medium=com&utm_campaign=morda")

    driver.implicitly_wait(1)

    driver.find_element(By.XPATH, "/html/body/header/div/div[2]/div[1]/form/div[1]/span/span/button/div").click()
    driver.implicitly_wait(1)

    driver.find_element(By.XPATH, "/html/body/header/div/div[3]/div[1]/div[2]/div[2]/div[3]/button[2]").send_keys(Keys.CONTROL + "v")

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cbir-similar-title"]/a')))

    driver.find_element(By.XPATH, '//*[@id="cbir-similar-title"]/a').send_keys(Keys.ENTER)
    driver.implicitly_wait(1)


    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        
        time.sleep(1)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            try :
                driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/div[2]/div[2]/a').send_keys(Keys.ENTER)
                time.sleep(3)
            except :
                driver.execute_script('window.scrollTo(0, 0)')
                break
        last_height = new_height


    images = driver.find_elements(By.CSS_SELECTOR, ".serp-item__thumb.justifier__thumb")
    folder_path = similar.file_path_ent.get()
    time.sleep(1)

    count = 1
    for image in images:

        try:
            image.click() 
            time.sleep(1)
            imgUrl = driver.find_element(By.XPATH, "/html/body/div[14]/div[2]/div/div/div/div[3]/div/div/div[2]/div[1]/div[3]/div/img").get_attribute("src") 
            file_name = os.path.basename(similar.image_path_ent.get())
            image_path = os.path.join(folder_path, str(os.path.splitext(file_name)[0]) + f' {count}.jpg') 
            urllib.request.urlretrieve(imgUrl, image_path) 
            driver.find_element(By.CLASS_NAME, "MMViewerModal-Close").click()
            count = count + 1

            if count > int(similar.count_ComboBox.get()):
                break
        
        except:
            pass

    driver.quit()
    msgbox.showinfo("Info", "Success")




def Keyword_image_scraping():

    if keyword.background_chkvar.get() == 1: # Background
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        driver = webdriver.Chrome(options=options)


    elif keyword.background_chkvar.get() == 0: # Foreground
        
        driver = webdriver.Chrome(find_CD.chromedriver_path_ent())
        driver.set_window_size(740, 660)


    driver.get("https://www.google.co.kr/imghp?hl=ko&tab=wi&authuser=0&ogbl")

    driver.find_element(By.NAME, "q").send_keys(keyword.image_keyword_ent.get() + Keys.ENTER)


    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        
        time.sleep(1)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            try :
                driver.find_element(By.CSS_SELECTOR, '".mye4qd"').click()
                time.sleep(3)
            except :
                break
        last_height = new_height


    images = driver.find_elements(By.CSS_SELECTOR, ".rg_i.Q4LuWd")
    folder_path = keyword.file_path_ent.get()

    time.sleep(1)

    count = 1
    for image in images:

        try:
            image.click() 
            time.sleep(1)
            imgUrl = driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div[3]/div[1]/a/img[1]').get_attribute("src") 
            image_path = os.path.join(folder_path, str(keyword.image_keyword_ent.get()) + f' {count}.jpg')
            urllib.request.urlretrieve(imgUrl, image_path) 
            count = count + 1

            if count > int(keyword.count_ComboBox.get()):
                break

        except:
            pass


    driver.quit()
    msgbox.showinfo("Info", "Success")




def similar_image_search_disable():

    if keyword.file_path_ent.get() != '' or keyword.image_keyword_ent.get() != '' or keyword.count_ComboBox.get() != 'Image Count' or keyword.background_chkvar.get() != 1:
        similar.image_path_ent.configure(state="disabled")
        similar.image_path_ent.delete(0, END)
        similar.image_btn_askdir.configure(state="disabled")
        similar.file_path_ent.configure(state="disabled")
        similar.file_path_ent.delete(0, END)
        similar.file_btn_askdir.configure(state="disabled")
        similar.count_ComboBox.configure(state="disabled")
        similar.count_ComboBox.set("Image Count")

    else:
        similar.image_path_ent.configure(state="normal")
        similar.image_btn_askdir.configure(state="normal")
        similar.file_path_ent.configure(state="normal")
        similar.file_btn_askdir.configure(state="normal")
        similar.count_ComboBox.configure(state="normal")




def keyword_image_search_disable():

    if similar.image_path_ent.get() != '' or similar.file_path_ent.get() != '' or similar.count_ComboBox.get() != 'Image Count':
        keyword.image_keyword_ent.configure(state="disabled")
        keyword.image_keyword_ent.delete(0, END)
        keyword.file_path_ent.configure(state="disabled")
        keyword.file_path_ent.delete(0, END)
        keyword.file_btn_askdir.configure(state="disabled")
        keyword.count_ComboBox.configure(state="disabled")
        keyword.count_ComboBox.set("Image Count")
        keyword.background_chkbox.config(state="disabled")
        keyword.background_chkvar.set(0)

    else:
        keyword.image_keyword_ent.configure(state="normal")
        keyword.file_path_ent.configure(state="normal")
        keyword.file_btn_askdir.configure(state="normal")
        keyword.count_ComboBox.configure(state="normal")
        keyword.background_chkbox.config(state="normal")




def all_disable():

    keyword.image_keyword_ent.delete(0, END)
    keyword.image_keyword_ent.configure(state="disabled")
    keyword.file_path_ent.delete(0, END)
    keyword.file_path_ent.configure(state="disabled")
    keyword.file_btn_askdir.configure(state="disabled")
    keyword.count_ComboBox.set("Image Count")
    keyword.count_ComboBox.configure(state="disabled")
    keyword.background_chkvar.set(0)
    keyword.background_chkbox.config(state="disabled")


    similar.image_path_ent.delete(0, END)
    similar.image_path_ent.configure(state="disabled")
    similar.image_btn_askdir.configure(state="disabled")
    similar.file_path_ent.delete(0, END)
    similar.file_path_ent.configure(state="disabled")
    similar.file_btn_askdir.configure(state="disabled")
    similar.count_ComboBox.set("Image Count")
    similar.count_ComboBox.configure(state="disabled")





def all_enable():

    similar.image_path_ent.configure(state="normal")
    similar.image_path_ent.delete(0, END)
    similar.image_btn_askdir.configure(state="normal")
    similar.file_path_ent.configure(state="normal")
    similar.file_path_ent.delete(0, END)
    similar.file_btn_askdir.configure(state="normal")
    similar.count_ComboBox.configure(state="normal")
    similar.count_ComboBox.set("Image Count")

    keyword.image_keyword_ent.configure(state="normal")
    keyword.image_keyword_ent.delete(0, END)
    keyword.file_path_ent.configure(state="normal")
    keyword.file_path_ent.delete(0, END)
    keyword.file_btn_askdir.configure(state="normal")
    keyword.count_ComboBox.configure(state="normal")
    keyword.count_ComboBox.set("Image Count")
    keyword.background_chkbox.config(state="normal")
    keyword.background_chkvar.set(0)




def ignore_click(event):
    return "break"





class chromedriver_link():
    menu = Menu(root)
    root.config(menu=menu)

    menu_file = Menu(menu, tearoff=0) 
    menu_file.add_command(label="Download Chromedriver", command=link_chromedriver)
    menu.add_cascade(label="Info", menu=menu_file) 





class find_chromedriver():
    find_chromedriver_frame = LabelFrame(root, text="Find Chrome Driver")
    find_chromedriver_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    chromedriver_path_ent = Entry(find_chromedriver_frame)
    chromedriver_path_ent.pack(side="left", fill="x", expand="True", padx=5, pady=5)

    chromedriver_find_btn_askdir = Button(find_chromedriver_frame, padx=10, pady=5, height=1, text="path...", command=add_chromedriver_path)
    chromedriver_find_btn_askdir.pack(side="right", padx=5, pady=5)





class similar_image_search():

    image_frame = LabelFrame(root, text="Similar image Search")
    image_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    image_path_frame = LabelFrame(image_frame, text="Image Path")
    image_path_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    image_path_ent = Entry(image_path_frame)
    image_path_ent.pack(side="left", fill="x", expand="True", padx=5, pady=5)

    image_btn_askdir = Button(image_path_frame, padx=10, pady=5, height=1, text="path...", command=add_image_path)
    image_btn_askdir.pack(side="right", padx=5, pady=5)


    file_path_frame = LabelFrame(image_frame, text="File Path")
    file_path_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    file_path_ent = Entry(file_path_frame)
    file_path_ent.pack(side="left", fill="x", expand="True", padx=5, pady=5)

    file_btn_askdir = Button(file_path_frame, padx=10, pady=5, height=1, text="path...", command=similar_add_path)
    file_btn_askdir.pack(side="right", padx=5, pady=5)


    count_values = ["Image Count", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50"]
    count_ComboBox = ttk.Combobox(image_frame, height=5, values=count_values, state="readonly") 
    count_ComboBox.set("Image Count") 
    count_ComboBox.pack()




class keyword_image_search():

    image_frame = LabelFrame(root, text="Keyword image Search")
    image_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    image_keyword_frame = LabelFrame(image_frame, text="Keyword")
    image_keyword_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    image_keyword_ent = Entry(image_keyword_frame)
    image_keyword_ent.pack(side="left", fill="x", expand="True", padx=5, pady=5)


    file_path_frame = LabelFrame(image_frame, text="File Path")
    file_path_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    file_path_ent = Entry(file_path_frame)
    file_path_ent.pack(side="left", fill="x", expand="True", padx=5, pady=5)

    file_btn_askdir = Button(file_path_frame, padx=10, pady=5, height=1, text="path...", command=keyword_add_path)
    file_btn_askdir.pack(side="right", padx=5, pady=5)


    count_values = ["Image Count", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50"]
    count_ComboBox = ttk.Combobox(image_frame, height=5, values=count_values, state="readonly") 
    count_ComboBox.set("Image Count") 
    count_ComboBox.pack()

    background_chkvar = IntVar() 
    background_chkbox = Checkbutton(image_frame, text="백그라운드로 실행", variable=background_chkvar)
    background_chkbox.pack(pady=7)





info_label_1 = Label(root, text="Similar image search by Yandex.")
info_label_2 = Label(root, text="Keyword image search by Google.")
info_label_1.pack(pady=5)
info_label_2.pack()




btn_search = Button(root, width=15, height=2, text="Search", command=start_search)
btn_search.pack(side="right", padx=17)

btn_reset = Button(root, width=15, height=2, text="Reset", command=option_reset)
btn_reset.pack(side="left", padx=17)



find_chromedriver()
similar_image_search()
keyword_image_search()



find_CD = find_chromedriver()
similar = similar_image_search()
keyword = keyword_image_search()


all_disable()


find_CD.chromedriver_path_ent.bind("<KeyRelease>", lambda event: all_enable())
similar.image_path_ent.bind("<KeyRelease>", lambda event: keyword_image_search_disable())
similar.file_path_ent.bind("<KeyRelease>", lambda event: keyword_image_search_disable())
similar.count_ComboBox.bind("<<ComboboxSelected>>", lambda event: keyword_image_search_disable())
keyword.file_path_ent.bind("<KeyRelease>", lambda event: similar_image_search_disable())
keyword.image_keyword_ent.bind("<KeyRelease>", lambda event: similar_image_search_disable())
keyword.count_ComboBox.bind("<<ComboboxSelected>>", lambda event: similar_image_search_disable())
keyword.background_chkbox.bind("<ButtonRelease-1>", lambda event: ignore_click if keyword.background_chkbox["state"] == "disabled" else similar_image_search_disable())







root.mainloop()