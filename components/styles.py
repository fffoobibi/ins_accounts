# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 16:18
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : styles.py
# @Software: PyCharm
from enum import Enum


class Sh(str, Enum):
    chapter_list_style = ''' 
        QListWidget::Item:hover:active{background-color: rgba(153, 149, 149, 80);color:#CCCCCC;border:none}
        QListWidget::Item{color:#CCCCCC; border:none;margin-left:10px}
        QListWidget::Item:selected{background-color: black;color: #CC295F}
        QListWidget{outline:0px; background-color: transparent; border:none}
    '''  # chapters_widget listwidget

    vertical_scroll_style = '''
        QScrollBar:vertical {background: black; padding: 0px;border-radius: 3px; max-width: 12px;}
        QScrollBar::handle:vertical {background: rgba(153, 149, 149, 80);min-height: 20px;border-radius: 3px;}
        QScrollBar::add-page:vertical {background: none;}
        QScrollBar::sub-page:vertical {background: none;}
        QScrollBar::add-line:vertical { background: none;}
        QScrollBar::sub-line:vertical {background: none; }
    '''  # more_widget scrollarea

    hori_scroll_style = '''
        QScrollBar:horizontal {background: black; padding: 0px;border-radius: 3px; max-width: 12px;}
        QScrollBar::handle:horizontal {background: rgba(153, 149, 149, 80);min-height: 20px;border-radius: 3px;}
        QScrollBar::add-page:horizontal {background: none;}
        QScrollBar::sub-page:horizontal {background: none;}
        QScrollBar::add-line:horizontal { background: none;}
        QScrollBar::sub-line:horizontal {background: none; }
    '''  # more_widget scrollarea

    upload_scroll_style = '''
        QScrollBar:horizontal {background: #E4E4E4;padding: 0px;border-radius: 3px;max-height: 5px;}
        QScrollBar::handle:horizontal {background: gray;min-width: 20px;border-radius: 3px;}
        QScrollBar::handle:horizontal:hover {background: #426BDD;}
        QScrollBar::handle:horizontal:pressed {background: #426BDD;}
        QScrollBar::add-page:horizontal {background: none;}
        QScrollBar::sub-page:horizontal {background: none;}
        QScrollBar::add-line:horizontal {background: none;}
        QScrollBar::sub-line:horizontal {background: none;}
       '''  # more_widget scrollarea

    pic_dialog_list_style = '''
            QListWidget::Item:hover:active{background-color: transparent; color:#CCCCCC;border:none}
            QListWidget::Item{color:#CCCCCC;border:none}
            QListWidget::Item:selected{ background-color: black;color: #CC295F}
            QListWidget{outline:0px; background-color: transparent; border:none}
        '''  # more_widget latest_dialog listwidget

    pic_dialog_style = '''
        QDialog{border:1px solid gray}QLabel{color:white; font-family: 微软雅黑}QPushButton{color:white;font-family: 微软雅黑}
        '''  # more_widget latest_dialog

    table_v_scroll_style = '''
        QScrollBar:vertical {background: #282A36;padding: 0px; border-radius: 3px;max-width: 8px;}
        QScrollBar::handle:vertical {background: #54555D; min-height: 20px; border-radius: 3px;}
        QScrollBar::handle:vertical:hover {background: #54555D;}
        QScrollBar::handle:vertical:pressed {background: #54555D;}
        QScrollBar::add-page:vertical { background: none;}
        QScrollBar::sub-page:vertical {background: none;}
        QScrollBar::add-line:vertical {background: none;}
        QScrollBar::sub-line:vertical {background: none;}
    '''

    table_h_scroll_style = '''
        QScrollBar:horizontal {background: #282A36;padding: 0px;border-radius: 3px;max-height: 8px;}
        QScrollBar::handle:horizontal {background: #54555D;min-width: 20px;border-radius: 3px;}
        QScrollBar::handle:horizontal:hover {background: #54555D;}
        QScrollBar::handle:horizontal:pressed {background: #54555D;}
        QScrollBar::add-page:horizontal {background: none;}
        QScrollBar::sub-page:horizontal {background: none;}
        QScrollBar::add-line:horizontal {background: none;}
        QScrollBar::sub-line:horizontal {background: none;}'''

    historycombobox_listview_style = '''
        QListView {outline: 0px;color: black;}
        QListView::item:hover {color: white;background-color: #5F89DF;}
        QListView::item{color: black;background-color: white;}'''

    historycombobox_style = '''
        QComboBox {font-family: "Microsoft YaHei";color: #000000;font-weight: bold;padding-left: 1px;border: 1px solid lightgray;border-radius:5px}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;}
        QComboBox::down-arrow{width:  30px;height: 30px;image: url(':/imgs/下拉箭头小.svg')}'''

    site_button_listview_style = '''
        QListView::item:hover{background: white;color:black;}
        QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
        QListView{outline:0px;background: transparent;border:1px solid lightgray}'''

    # menu_button_style = '''
    #     QPushButton{background-color:transparent; border: none; font-family: 微软雅黑}
    #     QPushButton:hover{color: #474746;background-color:#DBDBDB; border:none}
    #     QPushButton:pressed{color: #474746;background-color:#DBDBDB; border:none} '''
    #
    # menubar_button_style = '''
    #     QPushButton{background-color:transparent; border:none;text-align:right;font-family: 微软雅黑;font-size:9pt}
    #     QPushButton:hover{color: #474746;background-color:#DBDBDB}
    #     QPushButton:pressed{color: #474746;background-color:#DBDBDB}
    #     QPushButton::menu-indicator{image:none}'''
    #
    # font_combo_listwidget_style = '''
    #     QListWidget::Item:hover:active{background-color: rgba(153, 149, 149, 80); color:white}
    #     QListWidget{outline:0px; background-color: black; color: white; border: 1px solid lightgray}'''
    #
    # menu_style = '''
    #     QMenu {background-color : rgb(253,253,254);padding:5px;border:1px solid lightgray;}
    #     QMenu::item {font-size:9pt;color: black;background-color:rgb(253,253,254);padding: 10px 3px 8px 3px;margin: 3px 3px;}
    #     QMenu::item:selected {background-color : rgb(236,236,237);}
    #     QMenu::icon:checked {background: rgb(253,253,254);position: absolute;top: 1px;right: 1px;bottom: 1px;left: 1px;}
    #     QMenu::icon:checked:selected {background-color : rgb(236,236,237);background-image: url(:/space_selected.png);}
    #     QMenu::separator {height: 2px;background: rgb(235,235,236);margin-left: 10px;margin-right: 10px;}'''
    #
    # menubar_menu_style = '''
    #     QMenu{background-color : #BEBEBE;border:1px solid #BEBEBE;}
    #     QMenu::item {font-size:9pt;color: black;background-color:#BEBEBE;padding: 5px 3px 8px 3px;margin: 3px 3px;}
    #     QMenu::item:selected {background-color : #f4f4f4;}
    #     QMenu::separator {height: 2px;background: #CECDCD;margin-left: 2px;margin-right: 2px;}'''

    dynamic_menu_style = '''
            QMenu {background-color : %s;padding:5px;border:1px solid %s}
            QMenu::item {font-size:9pt;background-color: %s;color: %s;padding: 10px 3px 8px 3px;margin: 3px 3px;}
            QMenu::item:selected { background-color : red;}
            QMenu::icon:checked {background: rgb(253,253,254); position: absolute;top: 1px;right: 1px;bottom: 1px;left: 1px;}
            QMenu::separator {height: 2px;background: rgb(235,235,236);margin-left: 10px;margin-right: 10px;}'''

    submit_list_style = '''
        QListWidget::Item:hover{background-color:transparent;color:black}
        QListWidget::Item{/*border-bottom:1px solid rgb(212, 212, 212)*/}
        QListWidget::Item:selected{background-color: transparent;color:black;border-radius:5px}
        QListWidget{outline:0px; background-color: transparent;border-top:1px solid lightgray;border-bottom:1px solid lightgray;
            border-left:0px solid lightgray;border-right:0px solid lightgray;}'''

    green_v_scroll_style = '''
        QScrollBar:vertical {background: #E4E4E4;padding: 0px;border-radius: 3px;max-width: 12px;}
        QScrollBar::handle:vertical {background: lightgray;min-height: 20px;border-radius: 3px;}
        QScrollBar::handle:vertical:hover {background: #00BB9E;}
        QScrollBar::handle:vertical:pressed {background: #00BB9E;}
        QScrollBar::add-page:vertical {background: none;}
        QScrollBar::sub-page:vertical {background: none;}
        QScrollBar::add-line:vertical {background: none;}
        QScrollBar::sub-line:vertical {background: none;}'''

    list_page_style = '''
        QListWidget::Item:hover{background-color: #E9E9E9; color:black; border:none;border-bottom:1px solid rgb(212, 212, 212)}
        QListWidget::Item{border-bottom:1px solid rgb(212, 212, 212);border:none;color: lightgray}
        QListWidget{outline:0px; background-color: transparent;border:none}
        '''

    upload_list_page_style = '''
            QListWidget::Item:hover{background-color: transparent; color:black; border:none}
            QListWidget::Item{border: none;background-color: transparent;}
            QListWidget{outline:0px; background-color: transparent;border:none}
        '''

    history_list_page_style = '''
            QListWidget::Item:hover{background-color: lightgray; color:transparent; border:none}
            QListWidget::Item{border:1px solid white;background-color: white; border-radius:5px;color:transparent}
            QListWidget{outline:0px; background-color: transparent;border:none}
            '''

    icon_page_style = '''
        QListWidget::Item:hover{background-color:transparent; color:black}
        QListWidget::Item{border: none}
        QListWidget{outline:0px; background-color: transparent;border:none}'''

    fileter_listview_style = '''
        QListView::item:hover{background: white;color:black;border:none}
        QListView::item{border-bottom:1px solid rgb(212, 212, 212)}
        QListView::item:selected{background: lightgray;color:black}
        QListView{outline:0px;background: transparent;border:none}'''

    header_view_style = """
        QHeaderView::section           
        {        
            border-right: 0px solid white;
            border-left:0px solid white;  
            border-top:none;
            border-bottom: none;    
            background-color:#383A46;                
        }
         QHeaderView           
        {   color:white;
            font-family: 微软雅黑;
            border-right: 0px solid white;
            border-left: 0px solid white;  
            border-top: none;
            border-bottom: none;    
            background-color:#383A46;     
            font-weight: bold              
        }
    """

    header_view_style2 = """
        QHeaderView::section           
        {        
            text-align: left;
            border-right: 0px solid white;
            border-left:0px solid white;  
            border-top:none;
            border-bottom: none;    
            background-color:transparent;                
        }
         QHeaderView           
        {        
            border-right: 0px solid white;
            border-left: 0px solid white;  
            border-top: none;
            border-bottom: none;    
            background-color:transparent;                
        }
    """

    header_view_style3 = """
        QHeaderView::section           
        {        
            text-align: left;
            border-right: 0px solid white;
            border-left:0px solid white;  
            border-top:none;
            border-bottom: none;    
            background-color:transparent;                
        }
         QHeaderView           
        {        
            border-right: 0px solid white;
            border-left: 0px solid lightgray;  
            border-top: none;
            border-bottom: 0px solid lightgray;    
            background-color:transparent;                
        }
    """

    header_view_style4 = """
        QHeaderView::section           
        {  
        border:none               
        }
         QHeaderView           
        {        
            border:none;
            font-size: 10pt;
            font-weight: bold              
        }
    """

    number_line_ok = """
    QLineEdit{border:2px solid #ADC3F4;
            border-radius: 3px;
            font-family: 微软雅黑;
            height:26px}
    QLineEdit:focus{
            border:2px solid rgb(122,161,245);
            }
    """

    number_line_fail = """
         QLineEdit{border:2px solid red;
                        border-radius: 3px;
                        font-family: 微软雅黑;
                        height:26px}
         QLineEdit:focus{
                        border:2px solid rgb(122,161,245);
                        }
    """

    bank_line_ok = """
        QComboBox {
                border:2px solid #ADC3F4;
                border-radius: 3px;
                height:26px;
                padding-left: 1px;}
        QComboBox:focus{
            border: 2px solid rgb(122,161,245)}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
                }
        QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
        QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}
    """

    bank_line_fail = """
        QComboBox {
            border:2px solid red;
            border-radius: 3px;
            height:26px;
            padding-left: 1px;}
        QComboBox:focus{
            border: 2px solid rgb(122,161,245)}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
            }
        QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
        QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}
                """

    StyleSheet = """
        /*标题栏*/
        /*最小化最大化关闭按钮通用默认背景*/
        #buttonMinimum,#buttonMaximum,#buttonClose {
            border: none;
            background-color:transparent

        }
        /*悬停*/
        #buttonMinimum:hover,#buttonMaximum:hover {
            color: white;
        }
        #buttonClose:hover {
            color: white;
        }
        /*鼠标按下不放*/
        #buttonMinimum:pressed,#buttonMaximum:pressed {
            background-color: Firebrick;
        }
        #buttonClose:pressed {
            color: white;
            background-color: Firebrick;
        }
    """


{'count': 61, 'list': [
    {'id': 101, 'payment_id': 0, 'account_id': 3, 'payment_type': 0, 'type': 1, 'status': 0, 'sn': '4165465454',
     'create_time': '2022-01-20 18:01', 'creator': 'SMIT', 'department_name': '海外业务部', 'account_name': '农业银行',
     'attachment_list': []},
    {'id': 99, 'payment_id': 0, 'account_id': 1, 'payment_type': 0, 'type': 1, 'status': 0, 'sn': '4165465454',
     'create_time': '2022-01-20 18:01', 'creator': 'SMIT', 'department_name': '海外业务部', 'account_name': 'aaa',
     'attachment_list': []},
    {'id': 97, 'payment_id': 0, 'account_id': 1, 'payment_type': 0, 'type': 1, 'status': 0, 'sn': '4165465454',
     'create_time': '2022-01-20 18:01', 'creator': 'SMIT', 'department_name': '海外业务部', 'account_name': 'aaa',
     'attachment_list': []},
    {'id': 95, 'payment_id': 0, 'account_id': 3, 'payment_type': 0, 'type': 1, 'status': 0, 'sn': '123456',
     'create_time': '2022-01-20 18:01', 'creator': 'SMIT', 'department_name': '海外业务部', 'account_name': '农业银行',
     'attachment_list': []},
    {'id': 93, 'payment_id': 0, 'account_id': 3, 'payment_type': 0, 'type': 1, 'status': 0, 'sn': '123456',
     'create_time': '2022-01-20 18:01', 'creator': 'SMIT', 'department_name': '海外业务部', 'account_name': '农业银行',
     'attachment_list': []},
    {'id': 91, 'payment_id': 0, 'account_id': 3, 'payment_type': 0, 'type': 1, 'status': 0, 'sn': '123456',
     'create_time': '2022-01-20 18:01', 'creator': 'SMIT', 'department_name': '海外业务部', 'account_name': '农业银行',
     'attachment_list': []},
    {'id': 89, 'payment_id': 0, 'account_id': 1, 'payment_type': 0, 'type': 1, 'status': 0, 'sn': '123456',
     'create_time': '2022-01-20 18:01', 'creator': 'SMIT', 'department_name': '海外业务部', 'account_name': 'aaa',
     'attachment_list': []}, {'id': 87, 'payment_id': 0, 'account_id': 1, 'payment_type': 0, 'type': 1, 'status': 0,
                              'sn': '202112221456000090587', 'create_time': '2022-01-20 16:01', 'creator': 'SMIT',
                              'department_name': '海外业务部', 'account_name': 'aaa', 'attachment_list': [
            {'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120165821_0_bd_0.jpg'},
            {'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120165821_1_bd_1.jpg'},
            {'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120165821_2_bd_2.jpg'},
            {'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120165821_3_bd_3.jpg'}]},
    {'id': 85, 'payment_id': 0, 'account_id': 3, 'payment_type': 5, 'type': 2, 'status': 1,
     'sn': 'PZ202201201647426564', 'create_time': '2022-01-20 16:01', 'creator': 'SMIT', 'department_name': '海外业务部',
     'account_name': '农业银行', 'attachment_list': []},
    {'id': 83, 'payment_id': 0, 'account_id': 1, 'payment_type': 0, 'type': 1, 'status': 0,
     'sn': '202112221456000090587', 'create_time': '2022-01-20 16:01', 'creator': 'SMIT', 'department_name': '海外业务部',
     'account_name': 'aaa',
     'attachment_list': [{'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120164712_0_bd_0.jpg'},
                         {'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120164712_1_bd_1.jpg'},
                         {'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120164712_2_bd_2.jpg'},
                         {'path': 'http://bdfiletest.baizhoucn.com/payment/202201/20220120164713_3_bd_3.jpg'}]}],
 'pages': 7, 'limit': '10'}
