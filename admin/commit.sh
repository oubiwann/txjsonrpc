# Note: this script is for use with a dual svn+bzr working directory created by
# and managed with bzr-svn.
#
# The working dir was created in the following manner:
#   mkbranch Divmod genetic-programming-2620
#   cd ~/lab/Divmod/branches/genetic-programming-2620/Evolver
#   bzr co . bzrtest
#   cd bzrtest
#
# It was then pushed to Launchpad with the following (the branch had already
# been registered via the web interface on launchpad.net and was empty):
#   bzr push lp:~oubiwann/txevolver/dev --use-existing-dir
#
# To avoid pulling down the massive number of revisions from the Divmod svn
# repository, commits are performed locally, after which pushes are made to
# both svn and bzr repositories:
#   bzr commit --local --file myCommitMessage
#   bzr svn-push svn+ssh://myRepo
#   bzr push lp:myProjectMain
#
# To avoid potential Combinator/Bazaar disasters, all work is being done in the
# local working dir called "bzrtest" -- when the code is ready for merging, I
# will cd ../, rm bzrtest, perform an svn update on the branch that
# Combinator created, unbranch, and commit (to trunk).
#
# As JP pointed out, the bzr-svn svn props will likely need to be removed, in
# the event that they could cause problems (and it may be desirable for simple
# aesthetic purposes). The following command seems to indicate that bze-svn
# doesn't add props to any of the files:
#   svn ls --recursive|xargs svn proplist
# Getting the props on the bzr-svn-controlled directory shows that the
# following props are set:
#   bzr:revision-info
#   bzr:file-ids
#   bzr:revision-id...
# Which can be removed with the following:
#   for PROP in `svn proplist|grep bzr`; do svn propdel $PROP; done
#
LIB=./adytum/
SVN=svn+https://twisted-jsonrpc.googlecode.com/svn/trunk
BZR='lp:~oubiwann/txjsonrpc/google-bzr-svn'
FLAG='skip_tests'
MSG=commit-msg
export PYTHONPATH=.:./test

function abort {
    echo "*** Aborting rest of process! ***"
    exit
}

function error {
    echo "There was an error committing/pushing; temp files preserved."
    abort
}

function localCommit {
    echo "Committing locally ..."
    bzr commit --local --file $MSG
}

function pushGoogleCode {
    echo "Pushing to Subversion now ..."
    bzr svn-push $SVN
}

function pushLaunchpad {
    echo "Pushing to Launchpad now ..."
    bzr push $BZR
}

function cleanup {
    echo "Push succeeded. Cleaning up temporary files ..."
    rm $MSG
    rm -rf _trial_temp
    rm test.out
    echo "Done."
}

bzr diff ChangeLog | \
    egrep '^\+' | \
    sed -e 's/^\+//g'| \
    egrep -v '^\+\+ ChangeLog' > $MSG
echo "Committing with this message:"
cat $MSG
echo
if [[ "$1" == "$FLAG" ]];then
    echo 'OK' > test.out
else
    # send the output (stdout and stderr) to both a file for checking and
    # stdout for immediate viewing/feedback purposes
    /home/oubiwann/lab/Twisted/trunk/bin/trial $LIB 2>&1|tee test.out
fi
STATUS=`tail -1 test.out|grep 'FAIL'`
if [[ "$STATUS" == '' ]];then
    if [[ "$1" == "FLAG" ]];then
        echo "Skipping tests..."
    else
        echo "All tests passed."
    fi
    if [[ "`cat $MSG`" == '' ]];then
        pushGoogleCode || error
    else
        localCommit && pushGoogleCode || error
    fi
    pushLaunchpad && cleanup || error
else
    abort
fi
