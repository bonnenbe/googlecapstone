import random


f = open('newstuff.xml', 'w')

f.write("<?xml version=\"1.0\"?>\n")

f.write("<changes>\n")

names = ["ben", "nick", "albert", "bgilmore", "antarus", "krelinga"]
priorities = ["routine", "sensitive"]

summaries = ["Hello.", "Greetings, traveller.",
             "I greet you.", "Greetings.", "Heh, greetings.", "Well met!",
             "Greetings, friend.",
             "You face Jaraxxus, Eredar Lord of the Burning Legion!",
             "The pleasure is mine.", "My greetings."]



for x in range(1,101):
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

    f.write("  <created_on>2014-02-16T20:3:39</created_on>\n")
    f.write("  <key>" + str(x) + "</key>\n")

    f.write("  <technician>" + name + "</technician>\n")

    f.write("  <summary>" + summaries[random.randint(0, len(summaries)-1)] \
            + "</summary>\n")

    f.write("  <layman_description></layman_description>\n")
    f.write(" </ChangeRequest>\n")

f.write("</changes>\n")

f.close()
