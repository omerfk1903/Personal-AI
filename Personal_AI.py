import json # json dosyasınsa veri işlemleri yapmak için kullanılıyor
import speech_recognition as sr 
from gtts import gTTS # yazıyı konuşmaya çeviriyor 
from playsound import playsound # metni sese çevirme 
from difflib import get_close_matches as Truth # Doğruluk oranı 
from os import remove,getcwd 
from os.path import exists # Dosya yol kontrol 
from random import randint # Rasgele sayı üretmek için kullanılır
from threading import Thread,Event #"" Çekirdek kontrol
from time import sleep # Beklme
from datetime import datetime as dt # Tarih bilgisi için kütüphane 

class CHAT_BOT :      

    def __init__(self,Esik_Data_Control,FunchControl,dataControl,Esik_Data_True,Input_diff_cont,vouse_cont,WhileControl,Thread_Sleep):
        
        # Kontrol
        self.FunchControl = FunchControl
        self.WhileControl = WhileControl
        self.Input_Diff_Cont = Input_diff_cont
        self.Vouse_Cont = vouse_cont
        self.Esik_Data_Control = Esik_Data_Control
        self.Esik_Data_True = Esik_Data_True
        self.Thread_Sleep = Thread_Sleep
        self.dataControl = dataControl

        # Veri girişleri için kullanılıyor.
        self.data =  {"SORU" : None , "CEVAP" : None} 
        self.PEOPLE = {"NAME" : None , "SURNAME" : None,"GENDER" : None,"IMAGE_PATH" : None,"COUNTREY" : None}
        
        # TANIMLAR
        self.stop_thread = False
        self.text = None # Boş giriş tanımı 
        Data_name = "\\Personal_AI_Data.json" # veritabanı ismi
        self.file_Path = getcwd() # Dosyanın bulunduğu konum
        #self.date = [out for out in str(dt.now()).split(" ")] # Tarih bilgisi

        self.file_Path = self.file_Path + Data_name

        # Çalıştırılacak kodların cmd komutları.
        self.cmdClear = ["cmd.exe","/k","cls"]

        # veri tabanı değişkene aktarılıyor.
        self.dataRead = self.Data_Read() 

        self.data_Control(self.dataRead,esik=self.Esik_Data_Control)

        # Güncel veritabanı bilgileri ekleniyor
        self.Update_Date_Ansver = [rst["SORU"] for rst in self.dataRead["SORULAR"]]

        # Tanıyıcı (Recognizer) nesnesini oluştur
        self.recognizer = sr.Recognizer()

        # Mikrofonu sürekli açık tut
        self.microphone = sr.Microphone(device_index=0)

        # Tetikleme işlemi 
        global event # global tanımlama yapılmıştır 
        event = Event()

        if exists(self.file_Path) : print(" Veritabanı dosyası bulundu. ")
        else : print(" Veritabanı dosyası bulunamadı ")

    def Data_Read(self) : # JSON DOSYASINDAKİ VERİLER OKUNUYOR
        with open(self.file_Path,"r",encoding="UTF-8") as self.fileRead : return json.load(self.fileRead) 
 
    def Data_Write(self,data) :  # json dosyasına istenilen veriler yazdırılıyor.Türkçe karakterlere uygun bir şekilde
        with open(self.file_Path,"w",encoding="UTF-8") as fileWrite : json.dump(data,fileWrite,indent=2,ensure_ascii=False) 
        self.dataRead = self.Data_Read() # veri tabanı değişkene aktarılıyor.
        #if self.dataControl : self.data_Control(self.dataRead,esik=self.Esik_Data_Control)

    def Answer_Truth(self,Answer,Answers,Esik) : # Girilen sorunun veritabanındaki karşılığını doğruluk ile buluyor.
        try : 
            rst = Truth(Answer,Answers,n=1,cutoff=Esik)
            return rst[0] if rst else None
        except : 
            print("Truth error")
            return None

    def result (self,Answer,Data) : 
        data = [out for out in Data if out != None or out != " "]
        for Answer_Rst in data :
            if Answer_Rst["SORU"].lower() == Answer.lower() :
                return Answer_Rst["CEVAP"]
        data.clear() 
        return None 
    
    def Microp(self) : # Mikrofondan ses tanımlaması yapılıyor
        event.set()
        print("Mikrofon açık... (Konuşmaya başlayabilirsiniz)")
        with self.microphone as source:
            #self.stop_thread = False
            while True:
                try:
                    print("Lütfen konuşun...")
                    self.recognizer.adjust_for_ambient_noise(source)  # Ortam gürültüsünü azalt
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                    self.text = self.recognizer.recognize_google(audio, language="tr-TR")
                    print(f"Söylediğiniz: {self.text}")
                except sr.UnknownValueError:
                    print("Ses anlaşılamadı, tekrar deneyin...")
                    continue
                except sr.RequestError:
                    print("Bağlantı hatası veya Google servisi çalışmıyor")
                    continue
                sleep(self.Thread_Sleep)
        print("Dinleme durduruldu.")
    
    def speak(self,string): # Gelen metin sese dönüştürülüyor.
        try : 
            # yazıyı cümleye çeviriyor  
            tts = gTTS(string,lang = 'tr')# string bir değer gelmeli 
            rand = randint(1,1000)# random sayı alıyor
            file =  getcwd() + "\\" + "audio-" + str(rand) +'.mp3'# mp3 çeviriyor 
            while(not exists(file)) : tts.save(file)        
            playsound(file)
            remove(file)
        except : 
            if exists(file) : remove(file)

    def HumanName_And_Gender(self,Input) :
        cmtMan = False # FEMALE threading kontrol için 
        cmtFEMALE = False # MAN threading kontrol için

        # Veritabanındaki bütün özel isimler aktarılıyor : Names
        HumansNames = self.dataRead["NAMES"][0]

        # Giriş
        Input = Input.lower() 
        #letter = str(list(Input)[0]).upper()
        letter = Input[0].upper()
        print(letter)
        Humans_Names_Letter = HumansNames[letter] # Harfler  

        # Çıkış
        self.Nameout = None

        def MALE(Input) : # Erkek
            global cmtFEMALE
            if isinstance(Humans_Names_Letter,dict) and "Male" in Humans_Names_Letter : # oluşturulan dizinin formatı doğrulanıyor.
                for NameMale in Humans_Names_Letter["Male"] :
                    if NameMale.lower() in Input : 
                        cmtFEMALE = True
                        self.Nameout = "Male" 
                    if cmtMan == True : break
                    sleep(self.Thread_Sleep)
            else : print("HATA: Humans_Names_Letter sözlük formatında değil veya 'Male' anahtarı bulunamadı!")
        
        def FEMALE(Input) : # Kız
            global cmtMan
            if isinstance(Humans_Names_Letter,dict) and "Female" in Humans_Names_Letter :
                for NameFemale in Humans_Names_Letter["Female"] : 
                    if NameFemale.lower() in Input :
                        cmtMan = True 
                        self.Nameout = "Female" 
                    if cmtFEMALE == True : break
                    sleep(self.Thread_Sleep)
            else : print("HATA: Humans_Names_Letter sözlük formatında değil veya 'Male' anahtarı bulunamadı!")
        
        Thread_MALE = Thread(target=MALE,args=(Input, ))
        Thread_Female = Thread(target=FEMALE,args=(Input, ))
    
        Thread_MALE.start()
        Thread_Female.start()

        Thread_MALE.join() 
        Thread_Female.join()

        if self.Nameout != None : return self.Nameout

    def Pointing_Control(self,Input) : # Cümle noktalama işaretleri kontrol .
        for out in self.dataRead["İMPORTANT"] : 
            for out2 in out : 
                if out2.lower() in Input.lower() : 
                    return out[out2]

    def data_Control(self,data,esik) : # Aynı verileri kaldırmak için kullanılıyor
        dataAnswer = data["SORULAR"] # Sorular verileri çekiliyor
        dataAnswerLen = len(dataAnswer) # dizi boyutu
        if dataAnswerLen > 1 :
            for out in dataAnswer :
                Update_Date_Ansver = [rst["SORU"].lower() for rst in dataAnswer if rst["SORU"] != None and rst["SORU"] != " " and rst["SORU"] != out["SORU"]] # SORU
                Update_Date_rst = [rst["CEVAP"].lower() for rst in dataAnswer if rst["CEVAP"] != None and rst["SORU"] != " " and rst["CEVAP"] != out["CEVAP"]] # CEVAP
                if self.Answer_Truth(out["CEVAP"].lower(),Update_Date_rst,Esik=self.Esik_Data_Control) or self.Answer_Truth(out["SORU"].lower(),Update_Date_Ansver,Esik=self.Esik_Data_Control) : 
                    dataRemoveİndex = dataAnswer.index(out) # Kaldırılacak elemanın konumu alınıyor
                    del dataAnswer[dataRemoveİndex]
                    dataAnswerLen = len(dataAnswer) # dizi boyutu ayarlanıyor
                Update_Date_rst.clear()
                Update_Date_Ansver.clear()
            self.Data_Write(data=data) # Değiştirilen dizi json dosysına aktarılıyor
            self.dataRead = self.Data_Read()
        else : print(" data_control() : Yeterli veri yok. ")

    def Voice_Get_Control(self,VoiceControl,Input) : # Ses seviyesi 
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        # Ses kontrolü için aygıtı al
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        if VoiceControl == "VOİCE_LEVEL_GET" :
            # Ses seviyesini al
            current_volume = volume.GetMasterVolumeLevelScalar()  # 0.0 ile 1.0 arasında bir değer döner
            print(f"Mevcut Ses Seviyesi: {current_volume * 100:.2f}%")
        
        if VoiceControl == "VOİCE_LEVEL_SET" :
            # Ses seviyesini %50'ye ayarla
            LEVEL = Input/100
            volume.SetMasterVolumeLevelScalar(LEVEL, None)  # 0.0 = sessiz, 1.0 = maksimum
            print(f"Ses seviyesi %{Input}'ye ayarlandı.")

    def Time_and_date_information(self,Answer) : # Tarih ve zaman bilgisi alınıyor.
        Answer = Answer.lower()
        Fulldate = [out for out in str(dt.now()).split(" ")]
        forBreak = False
        speakText =""

        if "tarih" in Answer : # Tarih bilgisi
            date = Fulldate[0].split("-") 
            SEANSON = self.dataRead["SEASONS"]
            for seasonsOut in SEANSON : 
                for months in SEANSON[seasonsOut] :
                    if SEANSON[seasonsOut][months] == date[1] : 
                        forBreak = True
                        break
                if forBreak == True : break
            speakText = f"{date[0]} in {months} ayının nın {date[2]} "
            print(f" Tarih : {Answer} ")

        if "zaman" in Answer or "saat" in Answer : # Zaman bilgisi
            time = Fulldate[1].split(":") 
            speakText = f"{time[0]} {time[1]} geçiyor "

        if self.Vouse_Cont and speakText != "" : self.speak(string=speakText)

        Fulldate.clear()

    def sentecent_control(self,Input) : # Cümledeki kelimeleri çıkartır ve cümlenin büyük küçük kontrolü edilir.
        letter = "" # Harfleri
        word = "" # Kelime , Cümle
        range = [] # Kelimeleri parçalı bir şekilde toplama
        InputSprite = str(Input).split(" ") # Giriş  cümlesini parçalama
        for InputSpriteWord in InputSprite : # Metni parçalıyor
            for outletter in InputSpriteWord : # Kelimeyi parçalama
                for letter in self.dataRead["ABC"] : # Veri tabanındaki harfleri
                    letter = list(letter.keys())[0].upper() 
                    if letter == outletter.upper() : 
                        station = (not bool(InputSprite.index(InputSpriteWord)) and not bool(InputSpriteWord.index(outletter)))
                        if station : WordLetter = outletter.upper() 
                        else : WordLetter = outletter.lower() 
                        word = word + WordLetter # Büyük harf
            if InputSpriteWord != "" : range.append(word) 
            word = ""
        for wordSprite in range : word = word + " " + wordSprite
        return (word,range)

    def CHAT_BOT(self) : # MAİN

        if self.Input_Diff_Cont == True : event.wait()

        while self.WhileControl :

            # Güncel veritabanı bilgileri ekleniyor.Boş bir girdi eklememesi için if kullanılmıştır.
            self.Update_Date_Ansver = [rst["SORU"] for rst in self.dataRead["SORULAR"] if rst["SORU"] != None and rst["SORU"] != " "] # SORU
            
            # Giriş işleminin nasıl yapılacağı belirleniyor.
            if self.Input_Diff_Cont == False : self.text = str(input("YOU : "))
            
            (self.text,ty) = self.sentecent_control(self.text)
 
            # Girilen verinin veri tabanındaki karşılığı eşik değerine ulaşıp ulaşmadığını verir
            rt1 = self.Answer_Truth(self.text,self.Update_Date_Ansver,Esik=self.Esik_Data_True)
    
            if rt1 : # Eşik değeri geçebilecek bir girdi var ise çalışır.

                rt2 = self.result(rt1,self.dataRead["SORULAR"])
                    
                AnswerAbouth = self.Pointing_Control(Input=rt2) # Cümlenin ne olduğu belirtiliyor
                    
                # Cümlede özel isim geçip geçmediği belirleniyor.Cinsiyet belirtiliyor                    
                #Gender = self.HumanName_And_Gender(self.text)
                #print(" Gender : ".format(Gender))

                self.Time_and_date_information(self.text) # Zaman tarih kontrol 
                
                if self.Vouse_Cont == True : self.speak(rt2) 

                print(f" BOT : {rt2} AnswerAbouth : {AnswerAbouth} ")

            else : # Eşik değerine uygun bir giriş yok ise cevap nasıl olmalı diye soru sorar .

                copyText = self.text

                if self.Input_Diff_Cont == False and self.Vouse_Cont == True : 
                    self.speak(string="Bu soruya nasıl cevap vermeliyim")
                    self.text = str(input("Bu soruya ne cavap verilir : "))
                elif self.Input_Diff_Cont == True and self.Vouse_Cont == True : 
                    self.speak(string="Bu soruya nasıl cevap vermeliyim")
                else : self.text = str(input("Bu soruya ne cavap verilir : "))

                if copyText != None and self.text != None :

                    # Cümlede özel isim geçip geçmediği belirleniyor.Cinsiyet belirtiliyor .
                    #Gender = self.HumanName_And_Gender(copyText)
                    #print(" Gender : ".format(Gender))

                    # Zaman ve tarih bilgisi .
                    self.Time_and_date_information(copyText)    

                    self.data["SORU"] = copyText
                    self.data["CEVAP"] = self.text
                    self.dataRead["SORULAR"].append(self.data)
                    self.Data_Write(self.dataRead)
    
            # Dizi boşaltılıyor geçici olarak
            self.Update_Date_Ansver.clear()
            
            sleep(self.Thread_Sleep)

    def threading_Start(self) : 

        self.Thread_CHAT_GPT = Thread(target=self.CHAT_BOT)
        self.Thread_Mic = Thread(target=self.Microp)
        
        self.Thread_CHAT_GPT.start()

        if self.Input_Diff_Cont == True :

            self.Thread_Mic.start()
            self.Thread_CHAT_GPT.join()
            self.Thread_Mic.join()

        else  : self.Thread_CHAT_GPT.join()
