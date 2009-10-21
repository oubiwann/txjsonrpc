. ./admin/defs.sh

getDiff ChangeLog > $MSG
echo "Committing with this message:"
cat $MSG
echo
if [[ "$1" == "$FLAG" ]];then
    echo 'OK' > test.out
else
    # send the output (stdout and stderr) to both a file for checking and
    # stdout for immediate viewing/feedback purposes
    ./admin/runExamples.py
    trial $LIB 2>&1|tee test.out
fi
STATUS=`tail -1 test.out|grep 'FAIL'`
if [[ "$STATUS" == '' ]];then
    if [[ "$1" == "FLAG" ]];then
        echo "Skipping tests..."
    else
        echo "All tests passed."
    fi
    checkBuild || error " ERROR: checkBuild failed"
    if [[ "$1" == "skip_svn" ]]; then
        echo "Skipping commit to $SVN ..."
    else
        pushGoogleCode || error " ERROR: pushGoogleCode failed"
    fi
    localCommit && cleanup || error "ERROR: localCommit failed"
else
    abort
fi
