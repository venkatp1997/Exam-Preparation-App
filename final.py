# -*- coding: utf-8 -*-
import Tkinter as tkinter 
import tkMessageBox
import tkFileDialog
import time
from subprocess import call
import random 
import nltk

import re
#########

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from fpdf import FPDF
import subprocess
import rake
import operator
########
from PyPDF2 import PdfFileReader

from pyPdf  import PdfFileWriter, PdfFileReader

root=tkinter.Tk()
root.minsize(width=300,height=500)
root.maxsize(width=300,height=500)
root.configure(background='light blue')
subjects=[]
drawn={}
global xx
global yy
xx=0
yy=250
time_between_pdfs=10
time_each_pdf=30
global endTick_flag
endTick_flag=0

def checkNoun(tokens,word):
    for i in tokens:
        if i[0]==word and ("NN" in i[1]):
            return 1
    return 0
def getSentence(l,index,key):
    start_index=0
    end_index=len(l)-1
    for j in range(index-1,0,-1):
        if "." in l[j]:
            start_index=j+1
            break
    for j in range(index+1,len(l),1):
        if "." in l[j]:
            end_index=j
            break
    global used_keys
    if (start_index,end_index) not in used_keys or l.count(used_keys[(start_index,end_index)])>l.count(key):
        used_keys[(start_index,end_index)]=key
def find_headings(filename):
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, "password")
    outlines = document.get_outlines()
    headings=[]
    for (level,title,dest,a,se) in outlines:
        headings.append(str(title))
    return headings

def getheights(filename):
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser, "password")
    outlines = document.get_outlines()
    heights=[]
    for (level,title,dest,a,se) in outlines:
        heights.append(dest[3])
    return heights


def find_text( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


def convertpdftext(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text



class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(0, 80, 180)
        self.set_fill_color(230, 230, 0)
        self.set_text_color(220, 50, 50)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name):
        txt = name#fh.read().decode('latin-1')
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, num, title, name):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(name)

class Subject:
    def __init__(self,name,x,y,index):
        self.pdfs=[]
        self.s_name=name
        self.x=x
        self.y=y
        self.index=index
        self.pdf_heads=[]
        self.button=tkinter.Button(root,text=self.s_name,command=self.openWindow)
        self.button.place(x=self.x,y=self.y)
        self.button1=tkinter.Button(root,text="▲",command=self.upPreference)
        self.button1.place(x=self.x+100,y=self.y)
        self.button2=tkinter.Button(root,text="▼",command=self.downPreference)
        self.button2.place(x=self.x+150,y=self.y)
    def upPreference(self):
        index=self.index
        if index>0:
            subjects[index-1].y+=50
            subjects[index].y-=50
            subjects[index-1].index+=1
            subjects[index].index-=1

            temp_subject=subjects[index-1]
            subjects[index-1]=subjects[index]
            subjects[index]=temp_subject

            subjects[index-1].newPos()
            subjects[index].newPos()
    def downPreference(self):
        index=self.index
        if index<(len(subjects)-1):
            subjects[index+1].y-=50
            subjects[index].y+=50
            subjects[index+1].index-=1
            subjects[index].index+=1

            temp_subject=subjects[index+1]
            subjects[index+1]=subjects[index]
            subjects[index]=temp_subject

            subjects[index+1].newPos()
            subjects[index].newPos()
    def newPos(self):
        self.button.place(x=self.x,y=self.y)
        self.button1.place(x=self.x+100,y=self.y)
        self.button2.place(x=self.x+150,y=self.y)

    def addPDF(self,window):
        window.destroy()
        self.pdf_heads.append(0)
        filename=tkFileDialog.askopenfilename(filetypes=[("PDF Files","*.pdf")])
        if len(filename)>0:
            self.pdfs.append(filename)
        self.openWindow()

    def openWindow(self):
        window=tkinter.Toplevel(root)
        window.minsize(width=300,height=300)
        window.maxsize(width=300,height=300)
        w=tkinter.Label(window,text="List of PDFs:")
        w.place(x=0,y=0)
        
        x=0
        y=20
        for i in self.pdfs:
            button1=tkinter.Button(window,text=i,command=lambda: self.openPDF(i))
            button1.place(x=x,y=y)
            y+=20
        button2=tkinter.Button(window,text='Add PDF',command=lambda: self.addPDF(window))
        button2.place(x=0,y=260)
    def openPDF(self,name):
        call(["evince",name])

# def addPDF():
#     tkMessageBox.showinfo("addPDF","addPDF1")
def startProgram():
    tkMessageBox.showinfo("startProgram","startProgram1")
def endProgram():
    tkMessageBox.showinfo("endProgram","endProgram1")
def valueGET(val1,window):
    global xx
    global yy
    new_subject=Subject(val1,xx,yy,len(subjects))
    yy+=50
    subjects.append(new_subject)
    window.destroy()
def valueGET1(val1,val2,window):
    time_between_pdfs=val1
    time_each_pdf=val2
    window.destroy()
def addSubject():
    window=tkinter.Toplevel(root)
    window.minsize(width=150,height=150)
    window.maxsize(width=150,height=150)

    window.withdraw()
    window.update_idletasks()
    x=(window.winfo_screenwidth() - window.winfo_reqwidth()) / 2
    y=(window.winfo_screenheight() - window.winfo_reqheight()) / 2
    window.geometry("+%d+%d" % (x,y))

    window.deiconify()
    L1=tkinter.Label(window,text="Name")
    L1.pack(side="left")
    E1=tkinter.Entry(window,bd=5)
    E1.pack(side="right")
    submit=tkinter.Button(window, text="Enter", width=5, command=lambda: valueGET(E1.get(),window))
    submit.place(x=40,y=90)
def addPDF(new_subject):
    new_subject.addPDF("new_pdf")
def launchSettings():
    window=tkinter.Toplevel(root)
    window.minsize(width=250,height=250)
    window.maxsize(width=250,height=250)

    L1=tkinter.Label(window,text="Time between PDFs")
    L1.place(x=0,y=0)
    E1=tkinter.Entry(window,bd=5)
    E1.place(x=150,y=0)
    
    L2=tkinter.Label(window,text="Time for each PDF")
    L2.place(x=0,y=50)
    E2=tkinter.Entry(window,bd=5)
    E2.place(x=150,y=50)

    submit=tkinter.Button(window, text="Enter", width=5, command=lambda: valueGET1(E1.get(),E2.get(),window))
    submit.place(x=40,y=90)
def endTick():
    global endTick_flag
    endTick_flag=1
def getNewPDF():
    if len(subjects)==0: return
    subject_tr=random.randint(0,len(subjects)-1)
    if len(subjects[subject_tr].pdfs)==0: return
    pdf_tr=random.randint(0,len(subjects[subject_tr].pdfs)-1)
    filename=subjects[subject_tr].pdfs[pdf_tr]
    part_tr=subjects[subject_tr].pdf_heads[pdf_tr]
    toread = PdfFileReader(file(filename, 'rb'))
    firstpage=0
    lastpage=0
    pagecount=0
    heights=getheights(filename)
    headings=find_headings(filename)

    for page in toread.pages:
            pagetext = page.extractText()
            if headings[part_tr] in pagetext:
                firstpage=pagecount
                break
            pagecount=pagecount+1

    for page in toread.pages:
            pagetext = page.extractText()
            if headings[part_tr+2] in pagetext:
                lastpage=pagecount
                break
            pagecount=pagecount+1
    output = PdfFileWriter()

    page = toread.getPage(firstpage)
    page.trimBox.lowerLeft = (5, 5)
    page.trimBox.upperRight = (600, heights[part_tr])
    page.cropBox.lowerLeft = (5, 5)
    page.cropBox.upperRight = (600, heights[part_tr])
    output.addPage(page)

    for i in range(firstpage+1,lastpage):
        page = toread.getPage(i)
        page.trimBox.lowerLeft = (5, 5)
        page.trimBox.upperRight = (600, 800)
        page.cropBox.lowerLeft = (5, 5)
        page.cropBox.upperRight = (600, 800)
        output.addPage(page)


    page = toread.getPage(lastpage)
    page.trimBox.lowerLeft = (5,heights[part_tr+2])
    page.trimBox.upperRight = (600, 800)
    page.cropBox.lowerLeft = (5, heights[part_tr+2])
    page.cropBox.upperRight = (600, 800)
    output.addPage(page)


    outputStream = file("out.pdf", "wb")
    output.write(outputStream)
    outputStream.close()
    process=subprocess.Popen(['xdg-open', 'out.pdf'])
    process.wait()
    getFeedback(filename,part_tr)
def radio(window):
    global apq
    global correct_ans
    no_of_correct=0
    for j in range(len(apq)):
        if(apq[j].get()==correct_ans[j]):
            no_of_correct+=1
    tkMessageBox.showinfo("Accuracy",str(no_of_correct) + " out of " + str(len(apq)) + " is correct!")
    global sec
    sec=time_between_pdfs
    global endTick_flag
    endTick_flag=0
    window.destroy()
def getFeedback(filename,part_tr):
    STOPLIST="words.txt"
    rake_object = rake.Rake(STOPLIST, 5, 1, 2)

    text = convertpdftext(filename)
    headings=find_headings(filename)
    out = find_text(text,headings[part_tr],headings[part_tr+2])
    
    text_tokenized=nltk.word_tokenize(text.decode('utf-8'))
    tagged = nltk.pos_tag(text_tokenized)
    head=headings[part_tr]

    keywords1 = rake_object.run(out) # change to out
    keywords=[]
    for i in keywords1:
        keywords.append(i[0])
    global used_keys
    used_keys={}
    searchwords=["is","called","named","in","as"]
    list_text=text.split()
    fill_blanks=[]
    for i in range(len(list_text)):
        if list_text[i] in searchwords:
            if i>0 and list_text[i-1] in keywords and checkNoun(tagged,list_text[i-1])==1:
                getSentence(list_text,i,list_text[i-1])
            if i>1 and list_text[i-1] != "." and list_text[i-2] in keywords and checkNoun(tagged,list_text[i-2])==1:
                getSentence(list_text,i,list_text[i-2])
            if i<len(list_text)-1 and list_text[i+1] in keywords and checkNoun(tagged,list_text[i+1])==1:
                getSentence(list_text,i,list_text[i+1])
            if i<len(list_text)-2 and list_text[i+1] != "." and list_text[i+2] in keywords and checkNoun(tagged,list_text[i+2])==1:
                getSentence(list_text,i,list_text[i+2])
    nouns=[]
    for i in tagged:
        if "NN" in i[1]:
            nouns.append(i[0])
    for (i,j) in used_keys.iteritems():
        fill_blanks.append((" ".join(list_text[i[0]:i[1]+1]),j))
    window=tkinter.Toplevel(root)
    window.minsize(width=1300,height=700)
    window.maxsize(width=1300,height=700)
    x=0
    y=20
    global apq
    apq=[]
    global correct_ans
    correct_ans=[0]*len(fill_blanks)
    k=0
    if len(fill_blanks)>5:
        fill_blanks=fill_blanks[:5]
    for i in range(len(fill_blanks)):
        apq.append(tkinter.IntVar())
        apq[i].set(i)
    for i in fill_blanks:
        w=tkinter.Label(window,text=i[0].replace(i[1],"_______"))
        w.place(x=x,y=y)
        y+=50
        correct_ans[k]=random.randint(0,3)
        for j in range(4):
            if j==correct_ans[k]:
                global apq
                gumb1=tkinter.Radiobutton(window,text=i[1],value=j,variable=apq[k])
            else:
                while True:
                    pq=random.randint(0,len(nouns)-1)
                    if len(nouns[pq])>=4:
                        to_write=nouns[pq]
                        break
                global apq
                gumb1=tkinter.Radiobutton(window,text=to_write,value=j,variable=apq[k])
            gumb1.place(x=x,y=y)
            x+=200
        y+=50
        x=0
        k+=1
    B_submit=tkinter.Button(window,text="Submit",command=lambda: radio(window))
    B_submit.place(x=0,y=550)
        # ans=raw_input('Enter answer: ')
        # if ans==i[1]:
        #     print "Correct!"
        # else:
        #     print "Incorrect!"
    used_keys={}
        # subprocess.call(["xdg-open", 'out.pdf'])
def submitOpt(j,correct_opt):
    if j==correct_opt:
        global correct
        correct+=1

# def update():
#     x=0
#     y=700
#     w=tkinter.Label(root,text="List of subjects:")
#     w.place(x=x,y=y)
#     y+=50
#     for i in subjects:
#         if i.s_name not in drawn:
#             B_temp=tkinter.Button(root,text=i.s_name,command=addPDF(i))
#             B_temp.place(x=x,y=y)
#             drawn[i.s_name]=1
#         y+=50
#     root.after(1000,update)

w=tkinter.Label(root,text="List of subjects:")
w.place(x=0,y=200)

B_addSubject=tkinter.Button(root,text="Add Subject",command=addSubject)
B_addSubject.place(x=0,y=10)

# B_addPDF=tkinter.Button(root,text="Add PDF",command=addPDF)
# B_addPDF.place(x=0,y=250)

# B_start=tkinter.Button(root,text="Start Program",command=startProgram)
# B_start.place(x=0,y=100)

B_end=tkinter.Button(root,text="End",fg='blue',command=endTick)
B_end.place(x=150,y=100)

B_settings=tkinter.Button(root,text="Settings",command=launchSettings)
B_settings.place(x=0,y=150)

w=650
h=650

ws=root.winfo_screenwidth()
hs=root.winfo_screenheight()

x=(ws/2)-(w/2)
y=(hs/2)-(h/2)
sec = time_between_pdfs

def tick():
    global sec
    sec -= 1
    global endTick_flag
    if sec<=0:
        getNewPDF()
        endTick_flag=1
        return 
    time['text'] = sec
    # Take advantage of the after method of the Label
    if endTick_flag==0:
        time.after(1000, tick)
def tick1():
    global endTick_flag
    endTick_flag=0
    tick()
time = tkinter.Label(root, fg='green',font=("Helvetica", 16))
time.pack()
tkinter.Button(root, fg='blue', text='Start', command=tick1).place(x=0,y=100)


root.mainloop()
