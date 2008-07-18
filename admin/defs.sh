LIB=txjsonrpc
NAME=txJSON-RPC
EGG_NAME=txJSON_RPC
#BZR=lp:txjsonrpc
BZR='lp:~oubiwann/txjsonrpc/main'
SVN=svn+https://twisted-jsonrpc.googlecode.com/svn/trunk
FLAG='skip_tests'
MSG=commit-msg
export PYTHONPATH=.:./test

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
    echo "There was an error committing/pushing; temp files preserved."
    abort
}

function cleanup {
    echo "Cleaning up temporary files ..."
    rm -rf $MSG _trial_temp test.out .DS_Store CHECK_THIS_BEFORE_UPLOAD.txt
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
    bzr svn-push $SVN && pushSucceed
}

function buildSucceed {
    echo "Build succeeded."
    echo "Cleaning up files ..."
    ./admin/clean.sh
    echo "Done."
    echo
}
