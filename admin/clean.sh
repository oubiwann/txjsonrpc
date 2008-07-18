. ./admin/defs.sh
find . -name "*pyc" -exec rm {} \;
rm -rf build dist $EGG_NAME.egg-info _trial_temp/
