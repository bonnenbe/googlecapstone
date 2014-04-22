import random
import datetime

f = open('newstuff.xml', 'w')

f.write("<?xml version=\"1.0\"?>\n")

f.write("<changes>\n")

names = ["ben@google.com", "nick@google.com", "albert@google.com", "bgilmore@google.com", "antarus@google.com", "krelinga@google.com"]
priorities = ["routine", "sensitive"]

#summaries = ["Hello.", "Greetings, traveller.",
#             "I greet you.", "Greetings.", "Heh, greetings.", "Well met!",
#             "Greetings, friend.",
#             "You face Jaraxxus, Eredar Lord of the Burning Legion!",
#             "The pleasure is mine.", "My greetings."]

summaries = ["Software updates", "Server update", "Server maintenance",
             "Switch maintenance", "Datacenter software upgrade",
             "Server update", "Database restructuring",
             "Routine switch maintenance", "Failover license services to atlanta."]


for x in range(1,1000):
    print x
    f.write(" <ChangeRequest>\n")

    name = names[random.randint(0, len(names)-1)]
    author = "  <author>" + name + "</author>\n"
    f.write(author)
    
    f.write("  <implementation_steps></implementation_steps>\n")
    f.write("  <audit_trail>W10=</audit_trail>\n")

    priority = "  <priority>" + \
               priorities[random.randint(0, len(priorities)-1)] + "</priority>\n"
    f.write(priority)

    f.write("  <key>" + str(x) + "</key>\n")

    f.write("  <technician>" + name + "</technician>\n")

    f.write("  <summary>" + summaries[random.randint(0, len(summaries)-1)] \
            + "</summary>\n")

    f.write("  <description></description>\n")

    f.write("  <layman_description></layman_description>\n")
    f.write("  <impact></impact>\n")
    f.write("  <communication_plan></communication_plan>\n")
    f.write("  <documentation></documentation>\n")
    f.write("  <tests_conducted></tests_conducted>\n")
    f.write("  <backout_plan></backout_plan>\n")
    f.write("  <risks></risks>\n")
    f.write("  <rationale></rationale>\n")
    
    
    
    initial = datetime.datetime(2014, 1, 1)
    
    create = initial + datetime.timedelta(random.randint(-200, 60), random.randint(0, 47)*30*60)
    
    f.write("  <created_on>"+create.isoformat()+"</created_on>\n")
    
    start = create + datetime.timedelta(random.randint(2, 14), random.randint(0, 47)*30*60)
    f.write("  <startTime>"+start.isoformat()+"</startTime>\n")
    
    end = start + datetime.timedelta(0, random.randint(0, 100)*30*60)
    f.write("  <endTime>"+end.isoformat()+"</endTime>\n")
    
    
    if end < datetime.datetime.today()+datetime.timedelta(5):
        f.write("  <status>approved</status>\n")
    else:
        f.write("  <status>created</status>\n")
    
    f.write(" </ChangeRequest>\n")

f.write("</changes>\n")

f.close()
