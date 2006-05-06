svn stat|egrep -v '.swp|.pyc|lib/os|lib/net'
for DIR in lib/config lib/os lib/net lib/patterns lib/util lib/workflow
    do
        svn stat $DIR|egrep -v '.swp|.pyc'
    done
