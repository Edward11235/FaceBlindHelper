import kivy
import threading
import time
from kivy.app import App
from kivy.uix.button import Button

class Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.counter = 0
    def run(self):
        while True:
            print("Thread is running "+str(self.counter))
            app.button.text = self.set_button(self.counter)
            app.button.text = str(self.counter)
            time.sleep(0.5)
    def count(self):
        self.counter += 1
        app.button.text = str(self.counter)
    def set_button(self, value):
        app.button.text = str(value)

class MyApp(App):
    def __init__ (self, thread_object):
        App.__init__(self)
        self.thread_object = thread_object
    def callback(self,instance):
        print('The button <%s> is being pressed' % instance.text)
        self.thread_object.count()
    def build(self):
        self.button = Button(text='Hello World')
        self.button.bind(on_press=self.callback)
        return self.button

thread = Thread()
thread.start()
app = MyApp(thread)
app.run()