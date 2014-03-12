#!/usr/bin/python
import json
import re
import sys
import time
import darpa_open_catalog as doc
from pprint import pprint

active_content_file = sys.argv[1]
data_dir = sys.argv[2]
build_dir = sys.argv[3]
darpa_links = sys.argv[4]
date = time.strftime("%Y-%m-%d", time.localtime())

print """
Active content file: %s
Data directory: %s
Build directory: %s
""" % (active_content_file, data_dir, build_dir)

print "Attempting to load %s" %  active_content_file
active_content = json.load(open(active_content_file))

splash_page = doc.catalog_page_header()
splash_page += doc.logo("")
splash_page += doc.catalog_splash_content()
splash_page += doc.splash_table_header()

for program in active_content:
  program_name = program['Program Name']
  program_page_filename = program_name + ".html"
  program_page = doc.catalog_page_header()
  software_columns = []
  if program['Program File'] == "":
    print "ERROR: %s has no program details json file, can't continue.  Please fix this and restart the build." % program_name
    sys.exit(1)
  else:
    print "Attempting to load %s" %  program['Program File']
    program_details = json.load(open(data_dir + program['Program File']))
 
    program_page += doc.logo("<a href=\"http://www.darpa.mil/Our_Work/I2O/\"' style=\"color: #EBAF00;\"class='programlink'>Information Innovation Office (I2O)</a>")
    if re.search('^http',program_details['Link']):
      program_page += "\n  <h2><a href='" + program_details['Link'] + "' class='programlink'>" + program_details['Long Name'] + "</a></h2>\n"
    else:
      program_page += "<h2>%s</h2>" % program_details['Long Name']
    
    #program_page += "<h3><a href=\"http://www.darpa.mil/Our_Work/I2O/\"' class='programlink'>Information Innovation Office</a></h3>"
    program_page += "<div class='left-paragraph'><p>%s<p>" % program_details['Description']

    program_page += "<p>Program Manager: %s<p>" % program_details['Program Manager']
    program_page += "<p>Contact: <a href='mailto:%s'>%s</a><p>" % (program_details['Program Manager Email'], program_details['Program Manager Email'])
    program_page += "<p>The content below has been generated by organizations that are partially funded by DARPA; the views and conclusions contained therein are those of the authors and should not be interpreted as necessarily representing the official policies or endorsements, either expressed or implied, of DARPA or the U.S. Government.</p>"

    if program['Software File'] != "":
      program_page += "<ul><li>The Software Table lists performers with one row per piece of software. Each piece of software has licensing information, a link to an external project page or contact information, and where possible a link to the code repository for the project.</li></ul>"
    if program['Pubs File'] != "":
      program_page += "<ul><li>The Publications Table contains author(s), title, and links to peer-reviewed articles related to specific DARPA programs.</li></ul>"
    program_page += "<p>Report a problem: <a href=\"mailto:opencatalog@darpa.mil\">opencatalog@darpa.mil</a></p>"
    program_page += "<p>Last updated: %s</p></div>" % date
    if 'Image' in program_details.keys():
      if program_details['Image'] != "":
        program_page += "\n<div class='right-image'><img src=\"%s\"/></div>" % program_details['Image']
    
    banner = ""
    program_link = "<a href='%s'>%s</a>" % (program_page_filename, program_details['DARPA Program Name'])
    if program['Banner'].upper() == "NEW":
      banner = "<div class='wrapper'><a href='%s'>%s</a><div class='ribbon-wrapper'><div class='ribbon-standard ribbon-red'>%s</div></div></div>"  % (program_page_filename, program_details['DARPA Program Name'], program['Banner'].upper())
    elif program['Banner'].upper() == "COMING SOON":
      banner = "<div class='wrapper'>%s<div class='ribbon-wrapper'><div class='ribbon-standard ribbon-blue'>%s</div></div></div>"  % (program_details['DARPA Program Name'], program['Banner'])		
    elif program['Banner'].upper() == "UPDATED":
      banner = "<div class='wrapper'><a href='%s'>%s</a><div class='ribbon-wrapper'><div class='ribbon-standard ribbon-green'>%s</div></div></div>"  % (program_page_filename, program_details['DARPA Program Name'], program['Banner'])		
    else:
     banner = "<a href='%s'>%s</a>" % (program_page_filename, program_details['DARPA Program Name'])
    splash_page += "<TR>\n <TD width=130> %s</TD>\n <TD>%s</TD>\n</TR>" % (banner, program_details['Description']) 
    software_columns = program_details['Display Software Columns']

  # This creates a hashed array (dictionary) of teams that have publications. We use this to cross link to them from the software table.
  pubs_exist = {}
  if program['Pubs File'] != "" and program['Software File'] != "":
      print "Attempting to load %s" %  program['Pubs File']
      pubs_file = open(data_dir + program['Pubs File'])
      pubs = json.load(pubs_file)
      pubs_file.close()
      #print "Attempting to load %s" %  program['Software File']
      #softwares = json.load(open(data_dir + program['Software File'])) 
      for pub in pubs:
        for team in pub['Program Teams']:
          pubs_exist[team] = 1

	
  ###### SOFTWARE
  # ["Team","Software","Category","Code","Stats","Description","License"]
  if program['Software File'] != "":
    program_page += "<div width=100%><h2>Software:</h2>"
    print "Attempting to load %s" %  program['Software File']
    softwares = json.load(open(data_dir + program['Software File']))   
    program_page += doc.software_table_header(software_columns)
    for software in softwares:
      for column in software_columns:
        # Team
        if column == "Team":
          program_page += "<TR>\n  <TD>"
          for team in software['Program Teams']:
            if team in pubs_exist:
              team += " <a href='#" + team + "'><img height=20 width=20 src='pubs.png'></a>"
            program_page += team + ", "
          program_page = program_page[:-2]
          program_page += "</TD>\n "
        # Software
        if column == "Software":
          elink = ""
          if 'External Link' in software.keys():
            elink = software['External Link']
          if re.search('^http',elink) and elink != "":
            if darpa_links == "darpalinks":
              program_page += "  <TD><a href='http://www.darpa.mil/External_Link.aspx?url=" + elink + "'>" + software['Software'] + "</a></TD>\n"
            else:
              program_page += "  <TD><a href='" + elink + "'>" + software['Software'] + "</a></TD>\n"
          else:
            program_page += "  <TD>" + software['Software'] + "</TD>\n"
        # Category
        if column == "Category":
          categories = ""
          if 'Categories' in software.keys():
            for category in software['Categories']:
              categories += category + ", "
            categories = categories[:-2]
          program_page += "  <TD>" + categories + "</TD>\n"
        # Instructional Material
        if column == "Instructional Material":
          instructional_material = ""
          if 'Instructional Material' in software.keys():
            instructional_material = software['Instructional Material']
          if re.search('^http',instructional_material):
            if darpa_links == "darpalinks":
              program_page += "  <TD><a href='http://www.darpa.mil/External_Link.aspx?url=" + instructional_material + "'> Documenation or Tutorial </a></TD>\n"
            else:
              program_page += "  <TD><a href='" + instructional_material + "'> Documenation or Tutorial </a></TD>\n"
          else:
            program_page += "  <TD>" + instructional_material + "</TD>\n"
        # Code
        if column == "Code":
          clink = ""
          if 'Public Code Repo' in software.keys():
            clink = software['Public Code Repo']
          program_page += "  <TD> " + clink + " </TD>\n"
        # Stats
        if column == "Stats":
          if 'Stats' in software.keys():
            if software['Stats'] != "":
              slink = software['Stats']
              program_page += "  <TD> <a href='stats/" + slink + "/activity.html'>stats</a> </TD>\n"
            else: 
              program_page += "  <TD></TD>\n"
          else:
            program_page += "  <TD></TD>\n"
    
        # Description
        if column == "Description":
          program_page += " <TD> " + software['Description'] + " </TD>\n"
        # License
        if column == "License":
          program_page += " <TD> " + software['License'] + " </TD>\n </TR>\n"
    program_page += doc.software_table_footer()

####### Publications
  if program['Pubs File'] != "":
    program_page += "<br><br><h2>Publications:</h2>"
    print "Attempting to load %s" %  program['Pubs File']
    pubs = json.load(open(data_dir + program['Pubs File']))
    program_page += doc.pubs_table_header()
    for pub in pubs:
      program_page += "<TR>\n  <TD>"
      for team in pub['Program Teams']:
        program_page += team + "<a name='" + team + "'>, "
      program_page = program_page[:-2]
      program_page += "</TD>\n  <TD>" + pub['Title'] + "</TD>\n"
      link = pub['Link']
      if re.search('^http',link) or re.search('^ftp',link):
        if darpa_links == "darpalinks":
          program_page += "  <TD><a href='http://www.darpa.mil/External_Link.aspx?url=" + link + "'>" + link + "</a></TD>\n"
        else:
          program_page += "  <TD><a href='" + link + "'>" + link + "</a></TD>\n"
      else:
        program_page += "  <TD>" + link + "</TD>\n"
      program_page += "</TR>\n"
    program_page += doc.pubs_table_footer() + "</div><br>\n"
	
  program_page += doc.catalog_page_footer()
  print "Writing to %s" % build_dir + '/' + program_page_filename
  program_outfile = open(build_dir + '/' + program_page_filename, 'w')
  program_outfile.write(program_page)

splash_page += doc.splash_table_footer()
splash_page += doc.catalog_page_footer()

splash_page_file = build_dir + '/index.html'
print "Writing to %s" % splash_page_file
splash_outfile = open(splash_page_file, 'w')
splash_outfile.write(splash_page)





























































