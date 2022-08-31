# Windows application for logging different type of events #  
Log any kind of events (e.g. meals, any kind of activities, smoking cigarettes, ...).  
Logged events can be presented in range of reports.

### Technologies ###
- language - Python 3
- GUI - Tkinter
- database - SQLite

### Functionality details ###
##### Settings #####
- Add new event type - enter name of an event type
- Delete event type - deletes existing event type from a pop-up list (do not delete existing database records)
- Add this event - choose event type, enter date and hour of an event (to be used for logging a past event)
- Delete last event - deletes last logged event
- Warning - minutes from last event - enter number of minutes, warning pop-ups if time from a last event is shorter

<img src="imgs\setting.jpg" title="settings" height="380" width="197"/>

##### Events #####
- list of all event's types
- push the button to log an event
- push 'Close app' button to close the application

<img src="imgs\events.jpg" title="event's types" height="380" width="197"/>

##### Analysis #####
- list of available reports, for report for a specific day enter a date
- push the button to generate a report
- push 'Hide report' button to close a report

<img src="imgs\report.jpg" title="reports" height="380" width="197"/>

<img src="imgs\report_1.jpg" title="report_1" height="380" width="407"/>
