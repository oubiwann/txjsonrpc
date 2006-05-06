svn diff ChangeLog | \
    egrep '^\+' | \
    sed -e 's/^\+//g'| \
    egrep -v '^\+\+ ChangeLog' > commit-msg
echo "Committing with this message:"
cat commit-msg
echo
if [[ "$1" == 'skip_tests' ]];then
    echo 'OK' > test.out
else
    python tests/test_all.py &> test.out
fi
STATUS=`tail -1 test.out|awk '{print $1}'`
if [[ "$STATUS" == 'OK' ]];then
    rm test.out
    if [[ "$1" == 'skip_tests' ]];then
        echo "Skipping tests..."
    else
        echo "All tests passed."
    fi
    echo "Committing to Subversion now..."
    svn commit --file commit-msg && \
        rm commit-msg || \
        echo "There was an error committing; message preserved."
else
    echo "*** Commit aborting! Test suite failed ***"
    cat test.out
fi
