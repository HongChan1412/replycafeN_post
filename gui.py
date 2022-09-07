from httpx import RequestNotRead
from ui import Ui_MainWindow
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from webdriver_manager.chrome import ChromeDriverManager
from PyQt5 import QtWidgets
from selenium import webdriver
import random
from urllib.request import urlopen  # 주소를 열기 위해 사용
from urllib.parse import quote_plus # 문자를 url에 알맞은 형태로 치환하기 위해 사용
from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
import datetime
import time
import re
import pandas as pd
import clipboard
from logger import __get_logger
logger = __get_logger()
mobile_headers = [
    'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
    'Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; SCH-I535 Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-G955U Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/5.4 Chrome/51.0.2704.106 Mobile Safari/537.36'
]
class Worker(QObject):
  finished = pyqtSignal()
  progress = pyqtSignal(str)
  progress_status = pyqtSignal(str)
  bot = pyqtSignal(str)
  quit_process = 0
  last_title = ""
  
  def get_stocks(market=None):
    market_type = ''
    if market == 'kospi':
        market_type = '&marketType=stockMkt'
    elif market == 'kosdaq':
        market_type = '&marketType=kosdaqMkt'
    elif market == 'konex':
        market_type = '&marketType=konexMkt'
    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?currentPageSize=5000&pageIndex=1&method=download&searchType=13{market_type}'.format(market_type=market_type)

    list_df_stocks = pd.read_html(url, header=0, converters={'종목코드': lambda x: str(x)})
    df_stocks = list_df_stocks[0]
    return df_stocks

  def replyACT(self, stocks, driver, replyUSER):
    try:
      finish_word = ['','.','~','!',':)','(:','^^','ㅎㅎ','ㅎ','~!','~~','!!'] 
      adverb = ['','항상 ','너무 ']
      start_word = ['','좋은 ','완벽한 ','정확한 ','멋진 ']
      thankyou = ['감사합니다','고맙습니다','감사해요','고마워요','얻어갑니다','얻어가네요']
      stock_word = ['종목분석 ','전망 ','종목 ','전망분석 ','정보 ','주가분석 ','주가정보 ','분석 ']
      bigdata_report = ['리포트 ','빅데이터 리포트 ','리포트 분석 ','리포트 정보 ']
      humor = ['웃기네요','웃고 갑니다','대박','대박이네요','ㅋㅋㅋㅋ','ㅋㅋㅋㅋㅋㅋㅋㅋ','와..','대박 ㅋㅋ','헐','헐..','신기신기','신기하네요..']
      hotissue_theme = ['뉴스 ','종목이슈 ','소식 ','정보 ','이슈 ','빠른뉴스 ','빠른종목이슈 ','빠른소식 ','빠른정보 ','빠른이슈 ']
      medal_stock = ['좋아보입니다','좋은것 같습니다','기대됩니다','매수해볼게요','매수해볼까요']
      stock_res = ['수고하셨습니다','감사합니다','덕분에 수익 났습니다','수익 감사합니다','좋은 종목들만 있네요','종목들이 괜찮네요','수익률 좋네요','수익률 좋습니다']
      open_stock = ['기대되는 종목이네요','오전에 살펴봐야 겠네요','단기로 좋은것 같습니다','단타로 좋아보입니다','단기로 좋네요','기대되네요','좋아보입니다','시초가 공략 해보겠습니다']
      join_greet = ['안녕하세요','환영합니다','반가워요','반갑습니다','정보 얻어가세요','유익한 정보 받아가세요','잘부탁드려요']
      trade_log = ['매매일지 감사합니다','성투하세요','파이팅 합시다','수고하셨어요','수고하셨어용','수고하셨습니다']
      market_conditions = ['뉴스 ','시황 ','뉴스 정보 ','시황 정보 ','시황 뉴스 ','소식 ','빠른정보 ','빠른소식 ','빠른뉴스 ','이슈 ','빠른이슈 ']
      stock_news = ['뉴스 ','뉴스 정보 ','시황 뉴스 ','소식 ','빠른정보 ','빠른소식 ','빠른뉴스 ','이슈 ','빠른이슈 ']
      stock_debate = ['전망 어떻게 보세요?','어떻게 될까요','어떻게 될까요..','어떻게 보시나요?','전망 궁금하네요','괜찮을려나..']
      
      emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                              "]+", flags=re.UNICODE)
      pageString = driver.page_source  
      bsObj = BeautifulSoup(pageString, 'html.parser')
      board = bsObj.find(class_="border_name").text
      user = bsObj.find(class_="end_user_nick").text
      content = bsObj.find(class_="content").text
      title = bsObj.find("h2",{'class':'tit'}).text.strip()
      reply = bsObj.find_all(class_="comment_list")
      comment = bsObj.find_all(class_="nick_name")
      self.progress.emit(f"\n제목: {title}\n게시판: {board}\n글쓴이: {user}")
      
      self.progress_status.emit(f"좋아요 클릭 시도")
      
      like = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div/a')
      if like.get_attribute("aria-pressed") == "false":
        driver.execute_script("arguments[0].click();", like)
        
      if replyUSER == user:
        return False
      
      for i in range(len(comment)):
        if replyUSER in comment[i].text:
          return False
      
      while True:
        
        if board == "빅데이터 [리포트]":
          if user == "빅데이터":
            txt = title.split("[")[0]
            ran_txt = random.randint(1,3)
            if ran_txt == 1:
              post = random.choice(start_word)+random.choice(bigdata_report)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
            elif ran_txt == 2:
              post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
            else:
              post = random.choice(start_word)+txt+" "+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
          else:
            return False

        elif board == "유머 게시판":
          post = random.choice(humor)
        
        elif board == "핫이슈 + 테마 이야기":
          if user == "특징주 분석":
            txt = title.split(" ")[0]
            ran_txt = random.randint(1,2)
            if ran_txt == 1:
              post = random.choice(start_word)+random.choice(hotissue_theme)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
            else:
              post = random.choice(start_word)+txt+" "+random.choice(hotissue_theme)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
          else:
            return False
          
        elif board == "[추천주] 동메달 종목":
          stock_word.append("종목추천 ")
          ran_txt = random.randint(1,2)
          if "결산" not in title:
            if ran_txt%2:
              if user == "5분주식":
                content = content.replace("\n","").replace(" ","").replace("\u200b","")
                start_index = content.find("🔍")
                last_index = content.find("✅",start_index)
                stock_name =  emoji_pattern.sub(r" ",content[start_index+1:last_index]).split(" ")[0]
                for i in range(len(stocks)):
                  if stocks['회사명'][i] == stock_name:
                    post = stock_name+" "+random.choice(medal_stock)+random.choice(finish_word)
              else:
                post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
            else:
              post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
          else:
            post = random.choice(stock_res)+random.choice(finish_word)
          
        elif board == "[추천주] 은메달 종목":
          stock_word.append("종목추천 ")
          ran_txt = random.randint(1,2)
          if "결산" not in title:
            if ran_txt%2:
              if user == "5분주식":
                content = content.replace("\n","").replace(" ","").replace("\u200b","")
                start_index = content.find("🔍")
                last_index = content.find("✅",start_index)
                stock_name =  emoji_pattern.sub(r" ",content[start_index+1:last_index]).split(" ")[0]
                for i in range(len(stocks)):
                  if stocks['회사명'][i] == stock_name:
                    post = stock_name+" "+random.choice(medal_stock)+random.choice(finish_word)
              else:
                post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
            else:
              post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
          else:
            post = random.choice(stock_res)+random.choice(finish_word)

        elif board == "[추천주] 금메달 종목":
          stock_word.append("종목추천 ")
          if "결산" not in title:
            post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
          else:
            post = random.choice(stock_res)+random.choice(finish_word)
            
        elif board == "[소액/단타] 시초가 종목":
          stock_word.append("종목추천 ")
          ran_txt = random.randint(0,1)
          ran_txt2 = random.randint(0,1)
          if ran_txt:
            if user == "주식사는법" or "주식스터디":
              stock = []
              start_index = content.find("#")
              last_index = content.find("시초가 공략후",start_index)
              for i in range(len(stocks)):
                if stocks['회사명'][i] in content[start_index+1:last_index]:
                  stock.append(stocks['회사명'][i])
              post = random.choice(stock)+" "+random.choice(open_stock)+random.choice(finish_word)
            else:
              if ran_txt2:
                post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
              else:
                post = random.choice(open_stock)+random.choice(finish_word)
          else:
            if ran_txt2:
              post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
            else:
              post = random.choice(open_stock)+random.choice(finish_word)
        
        elif board == "가입인사 l 변경인사":
          ran_txt = random.randint(0,1)
          post = random.choice(join_greet)+random.choice(finish_word)
          if ran_txt:
            post = user+"님 "+post
        
        elif board == "매매일지 / 수익인증":
          post = random.choice(trade_log)+random.choice(finish_word)
        
        elif board == "종목 토론방 (토론)":
          stock_cnt = 0
          stock_name = ""
          for i in range(len(stocks)):
            cnt = 0
            if f" {stocks['회사명'][i]}" in content:
              cnt += content.count(f" {stocks['회사명'][i]}")
            if f"{stocks['회사명'][i]} " in content:
              cnt += content.count(f"{stocks['회사명'][i]} ")
            if f" {stocks['회사명'][i]} " in content:
              cnt += content.count(f" {stocks['회사명'][i]} ")
            if cnt != 0 and stock_cnt <= cnt:
              stock_cnt = cnt
              stock_name = stocks['회사명'][i]
          if stock_name:
            post = stock_name+" "+random.choice(stock_debate)
          else:
            return False
        
        elif board == "▶주식 뉴스 모음":
          post = random.choice(stock_news)+random.choice(thankyou)+random.choice(finish_word)
        
        elif board == "▶주식 특징주 모음":
          post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
          
        elif board == "주식 스터디 시황":
          txt = title
          ran_txt = random.randint(0,1)
          post = random.choice(market_conditions)+random.choice(thankyou)+random.choice(finish_word)
          if ran_txt:
            if "장전" in txt:
              post = "장전 "+post
            elif "장중" in txt:
              post = "장중 "+post
            elif "장후" in txt:
              post = "장후 "+post
            else:
              return False

        elif board == "주식스터디 종목결산":
          post = random.choice(stock_res)+random.choice(finish_word)
       
        elif board == "▶VC/IPO/M&A/공모주":
          if user == "특징주 분석":
            if "뉴스" in title:
              post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
            else:
              post = random.choice(start_word)+random.choice(stock_word)+random.choice(adverb)+random.choice(thankyou)+random.choice(finish_word)
          else:
            return False
        else:
          return False
        
        now = time.localtime()
        now = "%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        self.progress_status.emit(f"댓글작성 시도")
        if post not in reply:
          now = time.localtime()
          now = "%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
          self.progress.emit(f"댓글: {post}")
          self.bot.emit(f"{now} \"{title}\" >> \"{post}\" 작성 완료")
          element = driver.find_element(By.CLASS_NAME, "write")
          driver.execute_script("arguments[0].scrollIntoView(true);", element)
          driver.execute_script("arguments[0].click();", element)
          time.sleep(2)
          element = driver.find_element(By.CLASS_NAME, "text_input_area")
          driver.execute_script("arguments[0].scrollIntoView(true);", element)
          driver.execute_script("arguments[0].click();", element)
          element.send_keys(post)
          element = driver.find_element(By.CLASS_NAME, "btn_done")
          driver.execute_script("arguments[0].scrollIntoView(true);", element)
          driver.execute_script("arguments[0].click();", element)
          time.sleep(2)
          driver.back()        
          break
      return True
    except Exception as e:
      return False
  
  def run(self):
    try:
      stocks = self.get_stocks()
      self.progress.emit("주식 정보 최신화 완료")
      self.progress.emit("\n"+"{0:=^96}".format("프로세스 시작")+"\n")
      chrome_options = webdriver.ChromeOptions()
      if self.proxyLIST:
        with open(self.proxyLIST, 'r') as proxyLists:
          d = proxyLists.readlines()
          fileLists = list(map(lambda e: e.strip("\n"), d))
          random.shuffle(fileLists)
          chrome_options.add_argument('--proxy-server=%s' %fileLists[0])
      chrome_options.add_experimental_option("prefs", {
          'profile.default_content_setting_values.notifications': 1,
          'profile.default_content_setting_values.clipboard': 1
      })
      chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
      chrome_options.add_argument(f"user-agent={random.choice(mobile_headers)}")
      chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
      chrome_options.add_argument('--start-maximized')
      driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
      self.progress.emit("크롬드라이버 설정 완료")
      driver.implicitly_wait(30)
      self.progress.emit("로그인 시도")
      driver.get("https://nid.naver.com/nidlogin.login")
      time.sleep(1)
      driver.execute_script("document.getElementsByName('id')[0].value = \'" + self.naverID + "\'")
      time.sleep(1)
      driver.execute_script("document.getElementsByName('pw')[0].value=\'" + self.naverPW + "\'")
      time.sleep(1)
      driver.find_element(By.XPATH,'//*[@id="log.login"]').click()
      time.sleep(1)
      if driver.current_url != "https://nid.naver.com/nidlogin.login":
        self.progress.emit("로그인성공")
        driver.get(self.cafeURL)
        self.progress.emit("카페 접속 완료")
        time.sleep(2)
        pageString = driver.page_source  
        bsObj = BeautifulSoup(pageString, 'html.parser')
        last_title = []
        replyUSER = bsObj.find(class_="nick").text
        self.bot.emit(f"닉네임: {replyUSER}\n")
        reply_cnt = 0
        while self.quit_process == 0:
          if reply_cnt >= 100:
            self.progress_status.emit("닉네임 변경 시도")
            modify_name = "https://m.cafe.naver.com/CafeMemberProfileModify.nhn?cafeId=29470508"
            driver.get(modify_name)
            time.sleep(2)
            edited_lines = []
            with open(self.nameLIST,encoding='UTF8') as f:
              file = f.read()
              lines = file.splitlines()
              change_name = random.choice(lines)
              self.bot.emit(f"{change_name}으로 닉네임 변경")
              for line in lines:
                if line == change_name:
                  continue
                edited_lines.append(line)
            with open(self.nameLIST,"w",encoding='UTF8') as f:
              for i in edited_lines:
                f.writelines(i+"\n")    
            self.bot.emit(f"메모장에 남은 닉네임 개수: {len(edited_lines)}")
            modify = driver.find_element(By.ID, "nickname")
            modify.click()
            for i in range(20):
              modify.send_keys(Keys.BACKSPACE)
            modify.send_keys(change_name)
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="modifyForm"]/fieldset/div[5]/button').click()
            time.sleep(2)
            driver.get(self.cafeURL)
            reply_cnt = 0
            replyUSER = change_name
          time.sleep(2)
          pageString = driver.page_source  
          bsObj = BeautifulSoup(pageString, 'html.parser')
          title = bsObj.find("strong",{'class':'tit'}).text
          if title not in last_title:
            element = driver.find_element(By.XPATH, '//*[@id="ct"]/div[1]/div/ul/li[1]/div/a[1]/strong')
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
            if self.replyACT(stocks, driver, replyUSER):
              now = time.localtime()
              now = "%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
              time.sleep(2)
              btn = driver.find_element(By.CLASS_NAME, "btn_aside")
              driver.execute_script("arguments[0].click();", btn)
              time.sleep(1)
              copy_url = driver.find_element(By.XPATH, '//*[@id="ct"]/div[1]/div[2]/div[3]/div[1]/ul/li[2]')
              copy_url.click()
              self.progress.emit(f"{now} >> 댓글 작성 완료\n게시글 >> {clipboard.paste()}")
              reply_cnt += 1
            else:
              now = time.localtime()
              now = "%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
              self.progress.emit(f"{now} >> 댓글 작성 불가")
            time.sleep(2)
            driver.back()
            time.sleep(2)
          else:
            now = time.localtime()
            now = "%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
            self.progress.emit(f"\n{now} >> 글 리젠 대기")
          last_title.append(title)
          start = datetime.datetime.now()
          end = start + datetime.timedelta(minutes=int(self.replyDELAY))
          while datetime.datetime.now() <= end:
            txt_list = ['／','ㅡ','＼','ㅣ']
            for i in txt_list:
              now = time.localtime()
              now = "%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
              self.progress_status.emit(f"{now} >> 새로고침 대기중{i}")
              time.sleep(0.2)
          self.progress_status.emit("")
          driver.refresh()
      else:
        self.progress.emit("로그인실패")
        driver.quit()
      driver.quit()
      self.finished.emit()
    except  Exception as e:
      self.progress.emit(f"※오류발생※\n{e.args}")
      logger.error(e.args)
      self.finished.emit()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
  def __init__(self) :
    try :
      super().__init__()
      QtWidgets.QMainWindow(self)
      self.setupUi(self)
      self.run_flag = 0
      self.naverId.returnPressed.connect(self.inputID)
      self.naverPw.returnPressed.connect(self.inputPW)
      self.loginChk.clicked.connect(self.inputID)
      self.loginChk.clicked.connect(self.inputPW)
      self.cafeUrl.returnPressed.connect(self.inputURL)
      self.cafeChk.clicked.connect(self.inputURL)
      self.delayChk_2.setDisabled(True)
      self.delayChk.activated.connect(self.selectDELAY)
      self.delayChk_2.returnPressed.connect(self.inputDELAY)
      self.proxycombo.activated.connect(self.selectPROXY)
      self.startPause.clicked.connect(self.runClicked)
      self.reset_bot.clicked.connect(self.botRESET)
      self.reset_log.clicked.connect(self.logRESET)
      self.nameList.clicked.connect(self.selectLIST)
      self.naverID = ""
      self.naverPW = ""
      self.cafeURL = ""
      self.replyDELAY = ""
      self.proxyOPT = ""
      self.proxyLIST = ""
      self.nameLIST = ""
    except Exception as e:
      logger.error(e.args)
  
  def progress_emit(self,text):
    self.botstatus.setPlainText(text)
  
  def progress_emited(self, text):
    self.log.append(text)
    
  def bot_emit(self, text):
    self.botinfo.append(text)
    
  def inputID(self):
    self.naverID = self.naverId.text()
  
  def inputPW(self):
    self.naverPW = self.naverPw.text()

  def inputURL(self):
    self.cafeURL = self.cafeUrl.text()
    
  def selectDELAY(self):
    self.replyDELAY = self.delayChk.currentText()
    if self.replyDELAY == "직접입력":
      self.delayChk_2.setEnabled(True)
      self.delayChk_2.setPlaceholderText("입력후 엔터")
    else:
      self.delayChk_2.setDisabled(True)
      self.delayChk_2.clear()
    
  def inputDELAY(self):
    self.replyDELAY = self.delayChk_2.text()
    
  def selectPROXY(self):
    try:
      self.proxyOPT = self.proxycombo.currentText()
      if self.proxyOPT == "IP 리스트 선택":
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "IP 리스트 선택","","Text (*.txt)")
        self.proxyLIST = fname[0]
        if not self.proxyLIST:
          self.proxycombo.setCurrentText("자체 IP 변경")
        else:
          self.progress_emited(f"IP 리스트 불러오기 완료 >> {fname[0]}")
    except Exception as e:  
      logger.error(e.args)  
    
  def selectLIST(self):
    try:
      fname = QtWidgets.QFileDialog.getOpenFileName(self, "닉네임 변경 리스트 선택","","Text (*.txt)")
      self.nameLIST = fname[0]
      self.progress_emited(f"닉네임 변경 리스트 불러오기 완료 >> {fname[0]}")
    except Exception as e:
      logger.error(e.args)
    
  def runClicked(self):
    if self.run_flag == 0:
      self.naverID = self.naverId.text()
      self.naverPW = self.naverPw.text()
      self.cafeURL = self.cafeUrl.text()
      if self.delayChk.currentText() == "직접입력":
        self.replyDELAY = self.delayChk_2.text()
      else:
        self.replyDELAY = self.delayChk.currentText()
      self.proxyOPT = self.proxycombo.currentText()
      if self.naverID == "":
        self.progress_emited("ID를 입력해주세요")
        return
      if self.naverPW == "":
        self.progress_emited("PW를 입력해주세요")
        return
      if self.cafeURL == "":
        self.progress_emited("URL를 입력해주세요")
        return
      if self.replyDELAY == "":
        self.progress_emited("댓글작성 간격을 입력해주세요")
        return
      if self.nameLIST == "":
        self.progress_emited("닉네임 변경 리스트를 선택해주세요")
        return
      self.botinfo.append(f"ID: {self.naverID}\nPW: {self.naverPW}\n카페주소: {self.cafeURL}\n댓글작성 간격: {self.replyDELAY}분\n프록시 선택: {self.proxyOPT}\n닉네임 변경 리스트 선택: {self.nameLIST}")
      self.startPause.setText('■')
      self.run_flag = 1
      self.thread = QThread()
      self.worker = Worker()
      self.worker.moveToThread(self.thread)
      self.thread.started.connect(self.worker.run)
      self.worker.finished.connect(self.thread.quit)
      self.worker.finished.connect(self.worker.deleteLater)
      self.thread.finished.connect(self.thread.deleteLater)
      self.worker.progress.connect(self.progress_emited)
      self.worker.progress_status.connect(self.progress_emit)
      self.worker.bot.connect(self.bot_emit)
      self.thread.start()
      self.thread.finished.connect(
        lambda :  self.progress_emited("\n"+"{0:=^95}".format("프로세스 종료 완료")+"\n")
      )
      self.thread.finished.connect(self.threadFinished)
      self.worker.naverID = self.naverID
      self.worker.naverPW = self.naverPW
      self.worker.cafeURL = self.cafeURL
      self.worker.replyDELAY = self.replyDELAY
      self.worker.proxyOPT = self.proxyOPT
      self.worker.proxyLIST = self.proxyLIST
      self.worker.nameLIST = self.nameLIST
    else:
      self.worker.quit_process = 1
      self.progress_emited("현재 수행 작업 후 종료 됩니다.") 

  def threadFinished(self):
    self.run_flag = 0
    self.startPause.setText("▶")

  def botRESET(self):
    self.botinfo.clear()
    self.naverID = ""
    self.naverPW = ""
    self.cafeURL = ""
    self.replyDELAY = ""
    self.proxyOPT = ""
    self.proxyLIST = ""
    
  def logRESET(self):
    self.log.clear()

if __name__ =="__main__":
  import sys
  app = QtWidgets.QApplication(sys.argv)
  ui = MainWindow()
  ui.show()
  sys.exit(app.exec_())