'''
Automation view
===============

The main class here is :class:`MyAutomationView`. It's a view that can be seen on the 
screen, alongside the control and signal views.

This view includes an automation list (:class:`AutomationListView`) and some 
buttons below.
AutomationListView implements a ListView, using a list adapter and an
args converter.
Each item in the list is actually a dialog for selecting and setting parameters
in the selected action. The dialog is shown on the screen by
:class:`AutomationItemView` and data is saved in :class:`AutomationItem`. 

AutomationItemView is a composite list item that includes (left to right):
- A button that shows the index number of that item in the list (1,2,3,etc.).
- A Spinner to let the user choose an action.
- A panel to hold the chosen action's parameters.

AutomationItem simply holds a list of possible actions (to populate the
spinner in AutomationItemView and a reference to the chosed action (with its
parameters).

:class:`Action` represents a runnable action, with its parameters. It has a
on_start method that holds the code that should be run for that action, and
a on_stop method, to be run when the user aborted the action. These are to be
implemented by sub-classes, such as :class:`ActionRunFile`. 

'''

from __future__ import division
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, AliasProperty
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import ListProperty
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.event import EventDispatcher
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from instrumentino.cfg import *
from instrumentino.screens import MyView
from instrumentino.screens.list_widgets import CompositeListItemMember,\
    ListItemNormalLabel, ListItemSpinner
from instrumentino.variables import Variable, AnalogVariablePercentage,\
    AnalogVariableView, VariablesListView
from kivy.uix.listview import CompositeListItem, ListItemButton, ListView

class AutomationItemView(CompositeListItemMember, CompositeListItem):
    '''A widget for an automation item
    '''
    
    def __init__(self, **kwargs):
        index = kwargs['index']
        data = kwargs['data']
        
        #TODO: I don't think it would work well if we have two action with the same name. Check and get it to work. 
        
        # Set the height according to the number of parameters we need to show
        kwargs['height'] = kwargs['height'] * len(data.chosen_action.parameters)
        
        # Set the sub-widgets
        cls_dicts = [{'cls': ListItemButton,
                      'kwargs': {'text': '{}'.format(index+1)} },
                     {'cls': ListItemSpinner,
                      'kwargs': {'values': [c().name for c in data.action_classes],
                                 'text': data.chosen_action.name} },
                    {'cls': VariablesListView,
                     'kwargs': {'variables': data.chosen_action.parameters,
                                'text':''}
                    },
                     ]
        kwargs['cls_dicts']=cls_dicts
        super(AutomationItemView, self).__init__(**kwargs)


class AutomationItem(EventDispatcher):
    '''A class for holding the data of an automation item
    '''
    
    action_classes = ListProperty()
    '''The possible action classes
    '''
    
    chosen_action = ObjectProperty()
    '''The currently chosen action
    '''
    
    def __init__(self, **kwargs):
        check_for_necessary_attributes(self, ['action_classes'], kwargs)
        self.chosen_action = self.chosen_action or self.action_classes[0]()
        
        super(AutomationItem, self).__init__(**kwargs)


class AutomationListView(ListView):
    '''A list of automation items.
    '''
    
    items = ListProperty()
    '''The current items in the automation list
    '''
    
    def __init__(self, **kwargs):
        args_converter = lambda index, data: {'data':data,
                                              'height': 30,
                                              'size_hint_y': None,}

        kwargs['adapter'] = ListAdapter(data=self.items,
                                        args_converter=args_converter,
                                        selection_mode='multiple',
                                        allow_empty_selection=True,
                                        cls=AutomationItemView)
        
        super(AutomationListView, self).__init__(**kwargs)


class MyAutomationView(BoxLayout, MyView):
    '''The Automation view allows the user to create and run lists of actions (called methods).
    '''
    
    action_classes = ListProperty()
    '''The possible action classes
    '''
    
    def __init__(self, **kwargs):
        check_for_necessary_attributes(self, ['action_classes'], kwargs)
        
        super(MyAutomationView, self).__init__(**kwargs)
        
    def add_item(self):
        '''Add an item to the list
        '''
        self.run_items_list.adapter.data.append(AutomationItem(action_classes=self.action_classes))
        self.run_items_list._trigger_reset_populate()
    
    def remove_item(self):
        '''Remove selected items from the list
        '''
        indices = set(item.parent.index for item in self.run_items_list.adapter.selection)
        new_list = [i for j, i in enumerate(self.run_items_list.adapter.data) if j not in indices]
        self.run_items_list.adapter.data = new_list
        
        self.run_items_list._trigger_reset_populate()
    
    def run_all(self):
        '''Run all items in the list
        '''
        for item in self.run_items_list.adapter.data:
            item.chosen_action.on_start()
            

class Action(EventDispatcher):
    '''An action to be performed in the system
    '''
    
    name = StringProperty()
    '''The action's name on the screen
    '''
    
    parameters = ListProperty()
    '''The parameters needed for this action
    '''

    on_start = ObjectProperty()
    '''The code to be executed for this action
    '''
    
    on_stop = ObjectProperty()
    '''The code to be executed when the action is stopped
    '''
    
    
    def __init__(self, **kwargs):
        check_for_necessary_attributes(self, ['on_start'], kwargs)
        self.name = self.name or create_default_name(self, use_index=False)
        
        # Automatically populate the parameters' list by collecting all of the "Variable" instances we have.
        self.parameters = get_attributes_of_type(self, Variable, kwargs)
        
        super(Action, self).__init__(**kwargs)
        

class ActionRunFile(EventDispatcher):
    '''An action that runs the actions stored in an action-list file
    '''
    
    name = 'Run file'

    def on_start(self):
        '''Load an action-list file and run it
        '''
        #TODO: implement
        print 'running file...'
        
 