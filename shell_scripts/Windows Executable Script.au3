
#CS
Run("Autexys Dispatcher.cmd")
RunWait("python source/dispatcher.py")
#CE


RunWait('"' & @ComSpec & '" /k ' & "cd source & python manager.py")