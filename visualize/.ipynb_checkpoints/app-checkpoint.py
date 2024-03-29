import datetime
import time
import traceback

import streamlit as st
from components.container import Container
from components.navbar import Navbar
from components.sidebar import Sidebar
from configs.constants import DATE_NOW, TIME_STRINGS, VIEW_MODES, OVERVIEW, RAW_DATA, ROUTINE_REPORT, TRANSIENT_REPORT
from configs.module_loader import *
from configs.tag_config import TagConfig
from utils.css_utils import local_css
from utils.influx_utils import check_status, collector_status
from utils.session import init_session, sess, update_session
from utils.view_utils import (cal_different_time_range, load_all_check,
                              load_data, load_irv_tags,
                              load_mp_transient_periods,
                              visualize_data_by_raw_data)
from views.container import (render_inspection, render_irv_report,
                             render_mp_transient_report,
                             render_outstanding_tags, render_overview)
from views.sidebar import render_sidebar


class App:
  def __init__(self):
    self.navbar = Navbar()
    self.sidebar = Sidebar()
    self.container = Container()
    self.tag_configs = {}
    self.sessions = {}
    self.init()

  def init_tag_configs(self):
    self.tag_configs["mp"] = TagConfig("assets/files/tags.yaml")
    self.tag_configs["lip"] = TagConfig("assets/files/lip_tags.yaml")

  def init_sessions(self):
    now = DATE_NOW()
    init_session(self, "tags", [])
    init_session(self, "missing_data", "NaN")
    init_session(self, "view_mode", OVERVIEW)
    init_session(self, "search_tags", "")
    init_session(self, "selected_device_name", "")
    init_session(self, "interpolated", False)
    init_session(self, "time_range", 0)
    init_session(self, "start_date", now)
    init_session(self, "end_date", now)
    init_session(self, "start_time", now.time())
    init_session(self, "end_time", now.time())
    init_session(self, "difference_time_range", cal_different_time_range())
    init_session(self, "chart_mode", "merge")
    init_session(self, "call_influx", False)
    init_session(self, "data", None)
    init_session(self, "harvest_rate", collector_status())
    init_session(self, "check_rate", check_status())
    init_session(self, "server_time", DATE_NOW().strftime("%Y-%m-%d %H:%M:%S"))
    init_session(self, "_selected_tag", None)
    init_session(self, "_selected_checks", {})
    init_session(self, "nFlags", None)
    init_session(self, "oFlags", None)
    init_session(self, "iFlags", None)
    init_session(self, "fFlags", None)
    init_session(self, "current_machine", "mp")
    init_session(self, "sampling_rate", "30s")

  def init(self):
    # Configuration
    st.set_page_config(page_title="Home", page_icon=":house:", layout="wide")
    st.markdown(local_css(path.join(path.dirname(__file__), "assets", "style.css")), unsafe_allow_html=True)
    # Init session
    self.init_sessions()
    # Init tag configs
    self.init_tag_configs()

  def render(self):
    with st.sidebar:
      self.sidebar.render(self, sess("current_machine"), self.tag_configs[sess("current_machine")].devices)

    try:
      if sess("call_influx"):
        print(sess("call_influx"))
        print("query data")
        update_session("call_influx", False)
        if sess("view_mode") == OVERVIEW or sess("view_mode") == RAW_DATA:
          if len(sess("tags")) > 0:
            load_data()
          else:
            load_all_check()
        elif sess("view_mode") == ROUTINE_REPORT:
          load_irv_tags()
        elif sess("view_mode") == TRANSIENT_REPORT:
          load_mp_transient_periods()
          #load_roc_tags()

      with st.container():
        self.navbar.render()
        self.container.render()
        st.empty()

      
        
    except Exception:
      traceback.print_exc()
      st.error("Noooo data found. Extend 'Time Range' to retrieve more data", icon="❗")
      update_session("data", None)