# This sample file adds an additional push button at the bottom of the large screen format of the Hermes radio.

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import time
import math, wx

from tinyrpc import RPCClient
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport

rpc_client = RPCClient(
    JSONRPCProtocol(),
    HttpPostClientTransport('http://192.168.80.2:8066')
)

hardrock_server = rpc_client.get_proxy()

from hermes.quisk_widgets import BottomWidgets as StandardWidgets

class BottomWidgets(StandardWidgets):	# Add extra widgets to the bottom of the screen
  def Widgets_0x06(self, app, hardware, conf, frame, gbs, vertBox):
    StandardWidgets.Widgets_0x06(self, app, hardware, conf, frame, gbs, vertBox)
    if conf.button_layout == "Small screen":
      pass	# We are not using the small screen
    else:
      self.tuneButton = app.QuiskCheckbutton(frame, self.OnTune, 'Tune')
      gbs.Add(self.tuneButton, (self.start_row+1, self.start_col), (1, 1), flag=wx.EXPAND)
      #gbs.Add(self.tuneButton, (self.start_row, 21), (1, 2), flag=wx.EXPAND)
      pa_szr = wx.BoxSizer(wx.HORIZONTAL)
      gbs.Add(pa_szr, (self.start_row+1, self.start_col + 1), (1, 18), flag=wx.EXPAND)
      pa_text_temperature = wx.StaticText(frame, -1, ' Temp 100DC XX', style=wx.ST_NO_AUTORESIZE)
      pa_size = pa_text_temperature.GetBestSize()
      pa_text_temperature.Destroy()
      self.pa_text_temperature = wx.StaticText(frame, -1, '', size=pa_size, style=wx.ST_NO_AUTORESIZE)
      self.pa_text_fwd_power = wx.StaticText(frame, -1, '', size=pa_size, style=wx.ST_NO_AUTORESIZE)
      self.pa_text_swr = wx.StaticText(frame, -1, '', size=pa_size, style=wx.ST_NO_AUTORESIZE)
      self.pa_text_band = wx.StaticText(frame, -1, '', size=pa_size, style=wx.ST_NO_AUTORESIZE)
      flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL
      pa_szr.Add(self.pa_text_temperature, 0, flag=flag)
      pa_szr.Add(self.pa_text_fwd_power, 0, flag=flag)
      pa_szr.Add(self.pa_text_swr, 0, flag=flag)
      pa_szr.Add(self.pa_text_band, 0, flag=flag)

  def OnTune(self, event):
    print ("Tune button pressed")
    result = hardrock_server.setTune()
    self.tuneButton.SetValue(False)
    print ("Tune finished")

  def UpdateText(self):
    super().UpdateText()
  
    result = hardrock_server.getStatus()
    if "pep" in result:
        self.pa_text_fwd_power.SetLabel(str(result["pep"]) + "(" + str(result["avg"]) + ")" + "W")
    else:
        self.pa_text_fwd_power.SetLabel("--W")
    if "temp" in result:
        self.pa_text_temperature.SetLabel(str(result["temp"]) + u'\u2103')
    else:
        self.pa_text_temperature.SetLabel("--" + u'\u2103')
    if "swr" in result:
        self.pa_text_swr.SetLabel("1:" + str(result["swr"]))
    else:
        self.pa_text_swr.SetLabel("-----")
    if "band" in result:
        self.pa_text_band.SetLabel("Band:" + str(result["band"]))
    else:
        self.pa_text_band.SetLabel("Band:?")

  def OnDataPAFwdPower(self, event):
    self.data_sizer.Replace(self.pa_text_data, self.pa_text_fwd_power)
    self.pa_text_data.Hide()
    self.pa_text_data = self.pa_text_fwd_power
    self.pa_text_data.Show()
    self.data_sizer.Layout()
  def OnDataPASwr(self, event):
    self.data_sizer.Replace(self.pa_text_data, self.pa_text_swr)
    self.pa_text_data.Hide()
    self.pa_text_data = self.pa_text_swr
    self.pa_text_data.Show()
    self.data_sizer.Layout()
  def OnDataPATemperature(self, event):
    self.data_sizer.Replace(self.pa_text_data, self.pa_text_temperature)
    self.pa_text_data.Hide()
    self.pa_text_data = self.pa_text_temperature
    self.pa_text_data.Show()
    self.data_sizer.Layout()

