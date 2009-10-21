LIB=txjsonrpc
NAME=txJSON-RPC
EGG_NAME=txJSON_RPC
#BZR=lp:txjsonrpc
BZR='lp:~oubiwann/txjsonrpc/main'
SVN=svn+https://twisted-jsonrpc.googlecode.com/svn/trunk
FLAG='skip_tests'
MSG=commit-msg

function getDiff {
    bzr diff $1 | \
        egrep '^\+' | \
        sed -e 's/^\+//g'| \
        egrep -v "^\+\+ ChangeLog"
}

function abort {
    echo "*** Aborting rest of process! ***"
    exit 1
}

function error {
    MSG=$1
    echo $MSG
    echo '(Temp files preserved.)'
    abort
}

function checkBuild {
    # this script is used to automatically check the build and make sure nothing
    # in the build process was broken before a checkin.
    echo
    echo "Checking build process ..."
    echo
    python setup.py build
}

function cleanup {
    echo "Cleaning up temporary files ..."
    find . -name "*pyc" -exec rm {} \;
    rm -rf $MSG \
        build \
        dist \
        _trial_temp \
        test.out \
        .DS_Store \
        CHECK_THIS_BEFORE_UPLOAD.txt \
        $EGG_NAME.egg-info \
        doctest.out
    echo "Done."
}

function localCommit {
    echo "Committing locally ..."
    bzr commit --local --file $MSG
}

function pushSucceed {
    echo "Push succeeded."
}

function pushLaunchpad {
    echo "Pushing to Launchpad now ($BZR) ..."
    bzr push $BZR && pushSucceed
    cleanup
}

function pushGoogleCode {
    echo "Pushing to Subversion (Google) now ..."
    bzr push $SVN && pushSucceed
}
