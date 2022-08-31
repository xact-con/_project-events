import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import db_manager as dbm
import time


class App(tk.Tk):  # CheckIt: check Problems from PyCharm
    """ tk. variables """  # CheckIt: add class doku
    wWidth, wHeight = 274, 500
    wReport = wWidth + 50
    tkFont = ('Calibri', '15')
    tkFontSettings = ('Calibri', '13')
    tkPadX, tkPadY = (5, 0), 3
    tkIPadX, tkIPadY = 3, 1
    ttkPadding = (5, 5, 5, 0)

    def __init__(self):
        super().__init__()
        ttk.Style().configure('.', font=self.tkFont, padx=10, pady=4, ipadx=3, ipady=1)
        ttk.Style().configure('TNotebook.Tab', font=('Calibri', '13'), padding=(8, 0))
        ttk.Style().configure('TButton', padding=(8, 0))
        ttk.Style().configure('Settings.TButton', font=self.tkFontSettings)
        ttk.Style().configure('TEntry')
        ttk.Style().configure('TLabel', font=('Calibri', '11'))
        ttk.Style().configure('Report.TLabel', font=('Courier', '11'))
        self.bind_class('TButton', '<Return>', lambda e: e.widget.event_generate('<space>'))

        self.geometry(f"{self.wWidth}x{self.wHeight}+100+45")
        self.resizable(False, False)
        self.title('Login events')
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.tabs = ttk.Notebook(self, width=250, height=self.wHeight-38, padding=(5, 0, 10, 5))
        self.tabs.pack(anchor='nw', padx=self.tkPadX, side='left')
        self.tabs.enable_traversal()

        self.reasons_frame = FrameEventType(self.tabs)
        self.reasons_frame.pack(anchor='nw', padx=self.tkPadX, pady=self.tkPadY)
        self.tabs.add(self.reasons_frame, text='events', underline=0)

        self.analysis_frame = FrameAnalysis(self.tabs)
        self.analysis_frame.pack(anchor='nw', padx=self.tkPadX, pady=self.tkPadY)
        self.tabs.add(self.analysis_frame, text='analysis', underline=0)

        self.settings_frame = FrameSetting(self.tabs)
        self.settings_frame.pack(anchor='nw', padx=self.tkPadX, pady=self.tkPadY)
        self.tabs.add(self.settings_frame, text='settings', underline=0)

        # self.tabs.select(2)  # CheckIt: to be deleted

        self.reportsFrame = FrameReports(self)
        self.reportsFrame.pack(anchor='nw')

    @staticmethod
    def convert_epoch_to_str_time(sec=None):
        """ Converts epoch time into time in format 'HH:MM'
           sec - argument in seconds (epoch time), default now
           """
        return time.strftime('%H:%M', time.localtime(sec))

    @staticmethod
    def convert_epoch_to_str_date(sec=None):
        """ Converts epoch time into date in format 'YYYY-MM-DD'
           sec - argument in seconds (epoch time), default now
           """
        return time.strftime('%Y-%m-%d', time.localtime(sec))

    @staticmethod
    def width_window(width):
        """ Resizes main window
            width [int] - Np. of pixels for reports
            """
        app.geometry(f"{app.wReport + int(width)}x{app.wHeight}+100+45")

    @staticmethod
    def close_app():
        def set_settings(setting_name, setting_value):
            select = dbm.dbManager().Select(f"SELECT * FROM settings WHERE setting='{setting_name}'")
            if len(select) == 1:
                dbm.dbManager().Execute(f"UPDATE settings SET value={setting_value} "
                                        f"WHERE setting='{setting_name}'")
            else:
                dbm.dbManager().InsertOne('settings', (setting_name, setting_value))

        set_settings('min_time', app.settings_frame.min_time.get())
        app.destroy()


class FrameEventType(ttk.Frame):
    """
    Filling frame 'reasons_frame' in with buttons for each reason
    based on all records from table 'reasons'
    METHODS
    insert_event (self, event)
        inserting event into table 'events' triggered by 'reasonBtn'
    """
    def __init__(self, parent):
        """ PARAMETERS all from master App class"""
        super().__init__()
        self.parent = parent
        self.configure(height=App.wHeight - 38, width=250, relief='groove', padding=App.ttkPadding)
        self.pack_propagate(False)
        select = dbm.dbSelect().Select(f"SELECT * FROM reasons")

        for i in select:
            reasonBtn = ttk.Button(self, text=i[0])
            reasonBtn.bind('<Button-1>', self.insert_event)
            reasonBtn.bind('<space>', self.insert_event)
            reasonBtn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        closeBtn = ttk.Button(self, text='Close app', command=App.close_app)  # CheckIt: add underline here and others
        closeBtn.pack(pady=App.tkPadY + 4, ipady=App.tkIPadY, ipadx=App.tkIPadX, anchor='e', side='bottom')

    @staticmethod
    def insert_event(event):
        """ inserting event into table 'events' triggered by 'reasonBtn'
        day last until 4.00 AM next day
        """
        last_time = dbm.dbManager().Select(f"SELECT epoch, date FROM events ORDER BY epoch DESC")
        time_since_last_event = time.time() - last_time[0][0]
        if time_since_last_event < int(app.settings_frame.min_time.get()) * 60 \
                and event.widget.cget('text') not in ("in row", "after meal"):
            if not tk.messagebox.askokcancel(
                    'Warning',
                    f'Only {int(time_since_last_event / 60)} minutes since last ''event\nAre you sure?',
                    default='ok'
            ):
                app.settings_frame.create_events_tab()
                return False
        hours_4 = 60 * 60 * 4
        if time_since_last_event < hours_4 and last_time[0][1] != app.convert_epoch_to_str_date():
            date_to_insert = last_time[0][1]
        else:
            date_to_insert = app.convert_epoch_to_str_date()
        record_event = (
            date_to_insert,
            app.convert_epoch_to_str_time(),
            time.time(),
            event.widget.cget('text')
        )
        dbm.dbManager().InsertOne('events', record_event)
        app.analysis_frame.analysis_1(date_to_insert)
        app.settings_frame.create_events_tab()


class FrameAnalysis(ttk.Frame):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.configure(height=App.wHeight - 38, width=250, relief='groove', padding=App.ttkPadding)
        self.pack_propagate(False)

        analysis1_date = tk.StringVar()
        analysis1_date.set(App.convert_epoch_to_str_date())

        analysis1_dateEntry = ttk.Entry(self, width=10, justify='center', font=App.tkFont, textvariable=analysis1_date)
        analysis1_dateEntry.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, padx=15, anchor='n')

        analysis1Btn = ttk.Button(
            self, text='Events during the day', command=lambda: self.analysis_1(analysis1_date.get()))
        analysis1Btn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        analysis2Btn = ttk.Button(self, text='Statistic per day', command=self.analysis_2)
        analysis2Btn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        analysis3Btn = ttk.Button(self, text='Date / event type matrix', command=self.analysis_3)
        analysis3Btn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        hide_reportsBtn = ttk.Button(self, text='Hide report', command=self.hide_report)
        hide_reportsBtn.pack(pady=App.tkPadY + 4, ipady=App.tkIPadY, ipadx=App.tkIPadX, anchor='e', side='bottom')

    def analysis_1(self, date):
        select = dbm.dbSelect().Select(f"SELECT date, time, reason, epoch FROM events "
                                       f"WHERE date = '{date}' "
                                       f"ORDER BY epoch"
                                       )
        app.reportsFrame.titleLblTxt.set(f"Events on {date}:")
        header = f"{'Time':7}{'Min.':^5}{'Event type':15}\n{'-' * 27}\n"
        row = ""
        prv_epoch = 0
        for i in select:
            if i == select[0]:
                minute = 0
                prv_epoch = i[3]
            else:
                minute = int((i[3] - prv_epoch) / 60)
                prv_epoch = i[3]
            row = f"{i[1]:7}{minute:>3}  {i[2]:15}\n" + row
        if len(select) >= 2:
            summary_avg = f"Average {int(((select[-1][3] - select[0][3]) / (len(select) - 1)) / 60)} min."
        else:
            summary_avg = ""
        summary = f"Total {len(select)} times\n{summary_avg}\n{'-' * 27}\n"
        report = ''.join([header, summary, row])
        self.selectsReportText_update(report, len(header))

    def analysis_2(self):
        select = dbm.dbSelect().Select(f"SELECT date, count(rowid), min(epoch), max(epoch) FROM events "
                                       f"GROUP BY date "
                                       f"ORDER BY date DESC"
                                       )
        app.reportsFrame.titleLblTxt.set(f"Events per day:")
        header = f"{'Date':12}{'#':^5}{'Min':^7}{'Max':^7}{'Avg':^5}\n{'-' * 42}\n"
        row = ""
        for i in select:
            mini = App.convert_epoch_to_str_time(i[2])
            maxi = App.convert_epoch_to_str_time(i[3])
            row = ''.join((row, f"{i[0]:12}{i[1]:^5}{mini:^7}{maxi:^7}{int(((i[3] - i[2]) / i[1]) / 60):^5}", f"\n"))
        report = header + row
        self.selectsReportText_update(report, len(header))

    def analysis_3(self):
        reasons = dbm.dbSelect().Select(f"SELECT reason FROM reasons ORDER by reason")
        case = "count(CASE WHEN reason == '" + \
               "' THEN reason END), count(CASE WHEN reason == '".join([i[0] for i in reasons]) + \
               "' THEN reason END)"
        select = dbm.dbSelect().Select(f"SELECT date, {case}, COUNT(reason) "
                                       f"FROM events "
                                       f"GROUP BY date "
                                       f"ORDER BY date DESC"
                                       )
        app.reportsFrame.titleLblTxt.set(f"Events per day and event type:")
        reasons_header_1 = ' '.join(
            (f"{' ' * 5}" if i[0].find(' ') == -1 else f"{i[0][:i[0].find(' ')]:^5.5}") for i in reasons)
        reasons_header_2 = ' '.join(
            (f"{i[0]:^5.5}" if i[0].find(' ') == -1 else f"{i[0][i[0].find(' ') + 1:]:^5.5}") for i in reasons)
        result = f"{' ' * 7}{reasons_header_1}{' ' * 6}\n{'Day':7}{reasons_header_2} {'Total':^5.5}\n" \
                 f"{'-' * (7 + len(reasons) * 6 + 6 - 1)}\n"
        for i in select:
            day = time.strftime(f'%b %d', time.strptime(i[0], '%Y-%m-%d'))
            result += f"{day:^7}" + ' '.join(f"{i[j]:^5}" for j in range(1, len(reasons) + 1)) + \
                      f" {str(i[-1]):^5.5}" + '\n'
        self.selectsReportText_update(result, len(f"{'-' * (7 + len(reasons) * 6 + 6 - 1)}\n") * 2)

    @staticmethod
    def hide_report():
        app.reportsFrame.selectsReportFrame.destroy()
        App.width_window(-50)

    @staticmethod
    def selectsReportText_update(report, report_width):
        report_width_pixels = int(((report_width - 2) / 2 * 9))
        app.reportsFrame.selectsReportFrame.destroy()
        App.width_window(report_width_pixels)
        app.reportsFrame.create_selectsReportFrame(report_width_pixels)
        app.reportsFrame.selectsReportText.insert('insert', report)
        app.reportsFrame.selectsReportText.config(state='disabled')
        app.reportsFrame.selectsReportText.focus()


class FrameSetting(ttk.Frame):
    """
    Filling 'settings_frame':
    - adding new reason (to be shown in 'reasons_frame')
        - 'reasonEntry' widget to type in 'reason name'
        - 'addReasonBtn' triggering 'add_new_reason' method
    - deleting existing reason
        - 'delReasonBtn' triggering delete of chosen reason from table 'reasons'
    - possibility to add historical event:
    - deleting last record from table 'events'

    METHODS
    add_new_reason (self):
        Inserts new reason into table 'reasons' triggered by 'addReasonBtn',
        then call create_events_tab(self).
    delete_reason(self):
        Deletes a reason from table 'reasons' triggered by 'delReasonBtn',
        then call create_events_tab(self).
    create_events_tab(self):
        Deletes and re-creates 'events' tab  and updates 'eventCombo' due to changed No. of records in 'reasons'.
    reasonEntry_in (event):
        Deletes default grey-out 'add new reason' triggered by focus in 'reasonEntry' widget.
    insert_past_event(self):
        Inserts event into table 'events' triggered by 'addEventBtn'.
        Validates date, time format and past event.
    delete_last_event(self):
        Deletes last record in table 'events'.
    actual_time_update(self, event):
        Updates time in 'timeEntry' widget.
    """
    def __init__(self, parent):
        """ PARAMETERS all from master App class"""
        super().__init__()
        self.parent = parent
        sFw, sFh = 250, App.wHeight - 38  # settings_frame width, height
        self.configure(width=sFw, height=sFh, relief='groove', padding=App.ttkPadding)
        self.pack_propagate(False)

        canvas = tk.Canvas(self, highlightthickness=0)
        canvas.place(x=0, y=0, width=sFw - 7, height=sFh - 8)

        scroll = ttk.Scrollbar(self, orient='vertical')
        scroll.place(x=sFw - 7 - 20, y=0, height=sFh - 8)

        frame = ttk.Frame(canvas)
        frame.pack(side="left", fill="both", expand=True)
        frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        canvas.create_window((0, 0), window=frame, anchor='nw')

        reasonLbl = ttk.Label(frame, text='Add / Delete event type')
        reasonLbl.pack(ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        delReasonBtn = ttk.Button(frame, text='Delete event type', style='Settings.TButton', command=self.delete_reason)
        delReasonBtn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        self.reasonEntry = ttk.Entry(frame, justify='center', foreground='light grey', font=App.tkFontSettings)
        self.reasonEntry.insert(0, 'add new event type')
        self.reasonEntry.bind('<FocusIn>', self.reasonEntry_in)
        self.reasonEntry.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        addReasonBtn = ttk.Button(
            frame, text='Add new event type', style='Settings.TButton', command=self.add_new_reason)
        addReasonBtn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        """ Add past event """
        eventLbl = ttk.Label(frame, text='Add past event')
        eventLbl.pack(ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        reasons_list = [i[0] for i in dbm.dbSelect().Select(f"SELECT * FROM reasons")]

        self.eventCombo = ttk.Combobox(frame, values=reasons_list, state='readonly', font=App.tkFontSettings,
                                       justify='center')
        self.eventCombo.current(0)
        self.eventCombo.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX)

        eventFrame = ttk.Frame(frame)
        eventFrame.pack()

        self.event_date = tk.StringVar()
        self.event_date.set(App.convert_epoch_to_str_date())

        dateEntry = ttk.Entry(
            eventFrame, width=10, justify='center', font=App.tkFontSettings, textvariable=self.event_date)
        dateEntry.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, padx=(0, 30), anchor='n', side='left')

        self.event_time = tk.StringVar()
        self.event_time.set(App.convert_epoch_to_str_time())

        timeEntry = ttk.Entry(
            eventFrame, width=5, justify='center', font=App.tkFontSettings, textvariable=self.event_time)
        timeEntry.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, anchor='n', fill='x')

        addEventBtn = ttk.Button(
            frame, text='Add this event', style='Settings.TButton', command=self.insert_past_event)
        addEventBtn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        lineSep2 = ttk.Separator(frame)
        lineSep2.pack(ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        deleteLastEventBtn = ttk.Button(
            frame, text='Delete last event', style='Settings.TButton', command=self.delete_last_event)
        deleteLastEventBtn.pack(pady=App.tkPadY, ipady=App.tkIPadY, ipadx=App.tkIPadX, fill='x')

        """ App settings """
        minTimeFrame = ttk.Frame(frame)
        minTimeFrame.pack()

        minTimeLbl = ttk.Label(minTimeFrame, text='Warning - minutes \nsince last event:', width=20, justify='left')
        minTimeLbl.pack(ipady=App.tkIPadY, ipadx=App.tkIPadX, side='left')

        self.min_time = tk.StringVar(value='999')
        select = dbm.dbManager().Select("SELECT value FROM settings WHERE setting='min_time'")
        if len(select) != 0:
            self.min_time.set(select[0][0])

        minTimeEntry = ttk.Entry(
            minTimeFrame, justify='center', width=3, font=App.tkFontSettings, textvariable=self.min_time)
        minTimeEntry.pack(pady=(App.tkPadY + 5, App.tkPadY), ipady=App.tkIPadY, ipadx=App.tkIPadX)

    def add_new_reason(self):
        """ Inserts new reason into table 'reasons' triggered by 'addReasonBtn',
        then delete FrameEventType, and re-create it with actual records.
        """
        dbm.dbManager().InsertOne('reasons', f"('{self.reasonEntry.get()}')")
        self.create_events_tab()

    def delete_reason(self):
        """ Deletes a reason from table 'reasons' triggered by 'delReasonBtn'. """
        list_reasons = tk.Toplevel()  # CheckIt: self or not self or self in init
        list_reasons.title('Deleting reason')

        list_reasonsLbox = tk.Listbox(list_reasons, selectmode='single', font=App.tkFontSettings)
        select = dbm.dbSelect().Select(f"SELECT * FROM reasons")
        for i in range(len(select)):
            list_reasonsLbox.insert(i - 1, f"{select[i - 1][0]}")
        list_reasonsLbox.pack()

        def delete_reason_confirm(*args):
            """ Deletes record from table 'reasons' and recreates 'events' tab, if confirmed. """
            reason_to_delete = f"'{list_reasonsLbox.get(list_reasonsLbox.curselection())}'"
            list_reasons.destroy()
            if tk.messagebox.askokcancel('Confirmation', f'Are you sure to delete reason: \n{reason_to_delete}',
                                         default='ok'):
                dbm.dbManager().DeleteRecord('reasons', 'reason', reason_to_delete)
                self.create_events_tab()

        list_reasonsLbox.bind('<<ListboxSelect>>', delete_reason_confirm)

    def create_events_tab(self):
        """ Deletes and re-creates 'events' tab and updates 'eventCombo'. """
        self.parent.forget(0)  # 'events' tab
        self.reasons_frame = FrameEventType(self.parent)
        self.reasons_frame.pack(anchor='nw', padx=App.tkPadX, pady=App.tkPadY)
        self.parent.insert(0, self.reasons_frame, text='events', underline=0)
        reasons_list = [i[0] for i in dbm.dbSelect().Select(f"SELECT * FROM reasons")]
        self.eventCombo.config(values=reasons_list)
        app.tabs.select(0)

    def insert_past_event(self):
        """ inserts event into table 'events' triggered by 'addEventBtn'
        validate date, time format and past event
        """
        evnt_date = self.event_date.get()
        evnt_time = self.event_time.get()
        try:
            time.strptime(' '.join([evnt_date, evnt_time]), '%Y-%m-%d %H:%M')
        except ValueError:
            tk.messagebox.showwarning("Wrong format", "Enter proper format:\n"
                                                      "date 'YYYY-MM-DD'\n"
                                                      "time 'HH:MM'")
        else:
            if time.mktime(time.strptime(' '.join([evnt_date, evnt_time]), '%Y-%m-%d %H:%M')) > time.time():
                tk.messagebox.showwarning("Only past events", "You entered future event")
            else:
                evnt_date_structure = time.strptime(evnt_date + evnt_time, '%Y-%m-%d%H:%M')
                if evnt_date_structure.tm_hour < 4:
                    evnt_date_insert = time.strftime(
                        '%Y-%m-%d', time.localtime(time.mktime(evnt_date_structure) - 60 * 60 * 4))
                else:
                    evnt_date_insert = evnt_date
                record_event = (
                    evnt_date_insert,
                    evnt_time,
                    time.mktime(time.strptime(' '.join([evnt_date, evnt_time]), '%Y-%m-%d %H:%M')),
                    self.eventCombo.get()
                )
                dbm.dbManager().InsertOne('events', record_event)

    @staticmethod
    def delete_last_event():
        """ Deletes last record in table 'events' """
        select = dbm.dbSelect().Select(f"SELECT date, time, reason "
                                       f"FROM events "
                                       f"WHERE rowid = (SELECT max(rowid) FROM events)"
                                       )
        if tk.messagebox.askokcancel('Confirmation', f"Are you sure to delete last event:\n"
                                                     f"Date:\t{select[0][0]}\n"
                                                     f"Time:\t{select[0][1]}\n"
                                                     f"Reason:\t{select[0][2]}",
                                     default='ok'
                                     ):
            dbm.dbManager().DeleteLast('events')

    def actual_time_update(self, event):  # CheckIt: to be deleted???
        """ Updates time in 'timeEntry' widget"""
        self.event_time.set(app.convert_epoch_to_str_time())

    def reasonEntry_in(self, event):
        """ 'reasonEntry' widget - deleting default grey-out 'add new reason' when focused in """
        event.widget.delete(0, 'end')
        event.widget.config(foreground='black')


class FrameReports(ttk.Frame):
    """
    Setting frame 'reports_frame' as base place for reports
    METHODS
    """
    def __init__(self, parent):
        """ PARAMETERS all from master App class"""
        super().__init__()
        self.parent = parent

        self.titleLblTxt = tk.StringVar()
        titleLbl = ttk.Label(self, justify='left', padding=(15, 4, 15, 3), textvariable=self.titleLblTxt)
        titleLbl.pack(anchor='nw')

        self.create_selectsReportFrame()

    def create_selectsReportFrame(self, width=0):
        report_width = App.wReport + width - 250
        self.selectsReportFrame = ttk.Frame(self, width=report_width, height=App.wHeight - 38)
        self.selectsReportFrame.pack(anchor='nw')
        self.selectsReportFrame.pack_propagate(False)

        self.selectsReportText = tk.Text(self.selectsReportFrame, background='#F0F0F0', relief='groove',
                                         border=2, font=('Courier', 11), wrap='none')
        self.selectsReportText.place(x=0, y=0, width=report_width - 35, height=App.wHeight - 38)

        selectReportScroll = ttk.Scrollbar(self.selectsReportFrame, orient='vertical')
        selectReportScroll.place(x=report_width - 35 - 20, y=2, height=App.wHeight - 38 - 4)

        self.selectsReportText.config(yscrollcommand=selectReportScroll.set)
        selectReportScroll.config(command=self.selectsReportText.yview)


if __name__ == "__main__":
    app = App()
    app.mainloop()
