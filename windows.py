import wx
import MYUSER
import stock2
import threading
import time
import W_ShowRateData
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures
from multiprocessing import cpu_count

class MyFrame(wx.Frame):
    def __init__(self, parent=None, id=-1, title=''):

        wx.Frame.__init__(self, parent, id, title, size=(600, 335))

        self.cores = multiprocessing.cpu_count()
        self.pool = ProcessPoolExecutor(max_workers=cpu_count())
        
        self.panel = wx.Panel(self)
        self.bt_run = wx.Button(self.panel, label='開始')
        self.bt_stop = wx.Button(self.panel, label='stop')
        self.bt_download = wx.Button(self.panel, label='下載歷史資料')
        self.bt_selectStocks = wx.Button(self.panel, label='程式選股')
        self.bt_showRateData = wx.Button(self.panel, label='報酬率圖')

        self.lbl_money = wx.StaticText(self.panel, label='初始資金: ')
        self.text_money = wx.TextCtrl(self.panel)
        self.text_money.SetValue("200000")

        self.lbl_sdate = wx.StaticText(self.panel, label='開始日期: ')
        self.tex_sdate = wx.TextCtrl(self.panel)
        self.tex_sdate.SetValue("20190101")
        
        self.contents = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_WORDWRAP)

        self.hbox = wx.BoxSizer()
        self.hbox.Add(self.lbl_money, flag=wx.EXPAND)
        self.hbox.Add(self.text_money, flag=wx.LEFT)
        self.hbox.Add(self.lbl_sdate, flag=wx.EXPAND)
        self.hbox.Add(self.tex_sdate, flag=wx.LEFT)
        
        self.hbox2 = wx.BoxSizer()
        self.hbox2.Add(self.bt_run, flag=wx.LEFT, border=5)
        self.hbox2.Add(self.bt_stop, flag=wx.LEFT, border=5)
        self.hbox2.Add(self.bt_download, flag=wx.LEFT, border=5)
        self.hbox2.Add(self.bt_selectStocks, flag=wx.LEFT, border=5)
        self.hbox2.Add(self.bt_showRateData, flag=wx.LEFT, border=5)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.hbox, flag=wx.EXPAND | wx.ALL, border=5)
        self.vbox.Add(self.hbox2, flag=wx.EXPAND | wx.ALL, border=5)
        self.vbox.Add(self.contents, proportion=1,
                        flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                        border=5)
        self.panel.SetSizer(self.vbox)

        self.bindBtn()

        self._MYUSER = MYUSER.MYUSER(0,{},False,self.tex_sdate.GetValue())

    def bindBtn(self):
        self.bt_run.Bind(wx.EVT_BUTTON, self.OnClicked)
        self.bt_stop.Bind(wx.EVT_BUTTON, self.OnStopClicked)
        self.bt_stop.Disable()
        self.bt_download.Bind(wx.EVT_BUTTON, self.OnDownloadClicked)
        self.bt_selectStocks.Bind(wx.EVT_BUTTON, self.OnSelectStocksClicked)
        self.bt_showRateData.Bind(wx.EVT_BUTTON, self.OnShowRateDataClicked)

    def OnShowRateDataClicked(self, event):
        app = wx.App()
        frame = W_ShowRateData.MyFrame(self, -1, 'W_ShowRateData.py')
        frame.SetDimensions(0,0,640,480)
        frame.Show()
        app.MainLoop()
        # stock2.ShowRateData(self._MYUSER)
        # t5 = threading.Thread(self.callShowRateData())
        # t5.start()

    def callShowRateData(self):
        stock2.ShowRateData(self._MYUSER)
    
    def goSallSelectStocks(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            executor.submit(self.callSelectStocks())

    def OnSelectStocksClicked(self, event):
        threading.Thread(target = self.goSallSelectStocks).start()
        # with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        #     executor.submit(self.callSelectStocks())
        # t4 = threading.Thread(self.callSelectStocks())
        # t4.start()


    def callSelectStocks(self):
        t1 = time.time()
        self.contents.AppendText("執行程式選股中...")
        self.contents.AppendText('\n')

        with concurrent.futures.ThreadPoolExecutor (max_workers=cpu_count()) as executor:
            data = executor.submit(stock2.getData_csv(self))
        # executor = ProcessPoolExecutor(max_workers=cpu_count())
        # executor.submit(stock2.getData_csv(self))
        # self.contents.AppendText("程式選出的股票代號:%s"%(str(data)))
        # self.contents.AppendText('\n')
        t2 = time.time()
        print('time elapsed: ' + str(round(t2-t1, 2)) + ' seconds')
        

    def OnDownloadClicked(self, event):
        threading.Thread(target = self.callDownload).start()
        # t3 = threading.Thread(self.callDownload())
        # t3.start()

    def callDownload(self):
        self.contents.AppendText("下載歷史資料中...")
        self.contents.AppendText('\n')

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            executor.submit(stock2.downloadStockData())

        self.contents.AppendText("資料下載完成")
        self.contents.AppendText('\n')

    def OnStopClicked(self, event):
        self.bt_stop.Disable()
        self._MYUSER.setStop(True)
        self.contents.AppendText("終止程式中請稍後...")
        self.contents.AppendText('\n')
        # self.pool.map(self.getIsStopStatus(),"")
        threading.Thread(target = self.getIsStopStatus).start()
        # t2 = threading.Thread(target = self.getIsStopStatus)
        # t2.start()
    
    def getIsStopStatus(self):
        while True:
            if self._MYUSER._isStopOk:
                self.bt_run.Enable(True)
                self.contents.AppendText("程式已終止!")
                self.contents.AppendText('\n')
                break
            else:
                self.contents.AppendText(".")
                time.sleep(1)


    def OnClicked(self, event):
        self.bt_run.Disable()
        self.contents.AppendText("初始資金:%s"%(self.text_money.GetValue()))
        self.contents.AppendText('\n')
        self._MYUSER = MYUSER.MYUSER(self.text_money.GetValue(),{},False,self.tex_sdate.GetValue())
        self._MYUSER.setMyFrame(self)
        threading.Thread(target = self.start).start()
        # self.t = threading.Thread(target = self.start)
        # self.t.start()
        self.bt_stop.Enable(True)

    def start(self):
        startDate = self.tex_sdate.GetValue()

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            executor.submit(stock2.getData_mysql(20150101,startDate,self._MYUSER,"csv"))
        
        self.bt_stop.Disable()
        self.bt_run.Enable(True)
        self.contents.AppendText("程式執行結束")
        self.contents.AppendText('\n')

if __name__ == "__main__":
    app = wx.App()
    MyFrame(None, title='Simple Editor').Show()
    app.MainLoop()
