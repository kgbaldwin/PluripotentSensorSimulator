'''from twisted.internet import task, reactor

class obj:
    def __init__(self):
        self.timer1 = task.LoopingCall(self.func1)
        self.timer2 = task.LoopingCall(self.func2)
        self.timer3 = task.LoopingCall(self.func3)
        self.timer4 = task.LoopingCall(self.func4)
        self.counter = 0

    def func1(self):
        print("func 1")

    def func2(self):

        print("func 2 " + str(self.counter))
        self.counter += 1

        if self.counter == 5:
            self.timer1.stop()

            self.timer3.start(3)

    def func3(self):
        print("3 func")
        self.timer3.stop()
        self.timer1.start(1)

    def func4():
        print("func 4")


test = obj()

test.timer1.start(1)
test.timer2.start(2)

reactor.run()

#timer4 = task.LoopingCall(func4)'''


# 3/23/23
# https://stackoverflow.com/questions/30841738/run-lua-script-from-python
# https://stackoverflow.com/questions/15374211/why-does-popen-communicate-return-bhi-n-instead-of-hi
import subprocess

#result = subprocess.check_output(['lua', '-l', 'demo', '-e', 'test("at", "p")'])
#print(result.strip().decode('ascii'))

result = subprocess.check_output(['lua', '-l', 'demo', '-e', 'mean({1,5,8,3,3})'])
print(result.strip().decode('ascii'))

#result = subprocess.check_output(['lua', '-l', 'demo', '-e', 'test2("a")'])
#print(result)


