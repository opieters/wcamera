import PIR

print "Testing PIR"

print "init function"
PIR.init()

print "reading some set values"
print PIR.conf
print PIR.camera
print PIR.run_complete

print "run function"
PIR.run()

print "delete function"
PIR.delete()

print "Done"
