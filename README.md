# S2PS   
## Introduction 

This project is essentially a rewrite of the III2PS desktop application.  
The purpose is to convert accounting data from the format produced by Sierra to a format that can be ingested by PeopleSoft.   
The project consists of a python script (s2ps.py) that can be called from the command line, and a web frontend written in PHP/HTML.

### Motivation
The motivation behind the rewrite is that the old program (III2PS), while still functional, tends to cause problems whenever it is deployed or changes need to be made.


III2PS issues:
- It's written in an old version of VB.NET, and requires a legacy environment to build
- It's a desktop application, so it needs to be installed on each individual's computer. 
- Any changes made to the source require that the program be re-built and re-deployed. 


S2PS advantages:
- Written in Python (commonly installed on severs, changes can be tested immediately) 
- Everything runs server side or in the browser (eliminates the deployment issue)

## Requirements

### Packages 

- Python 2.x (Tested with {v2.6.6, v2.7.6})
- PHP 5.x (Tested with {v5.5.9, v5.6.16})

## Installation (server side)
The repository configured such that the user's public_html directory can be symlinked to the repository directory and everything should "just work."

```
cd ~ 
git clone https://github.com/nihilanth41/s2ps.git
ln -s ~/s2ps ~/public_html
```

## Configuration 
Minimal configuration should be necessary. If there are issues check the following: 
- PHP is installed and configured correctly 
- [Per-user web directories are enabled] (https://httpd.apache.org/docs/trunk/howto/public_html.html) (Instructions may vary depending on OS/Distro) 
- ~/s2ps/uploads/ directory has permissions: drwxrwxr-x (775)
 - uploads/ directory has the web user as either the user-owner or group-owner   




