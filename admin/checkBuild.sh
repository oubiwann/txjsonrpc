# this script is used to automatically check the build and make sure nothing
# in the build process was broken before a checkin.
. ./admin/defs.sh
echo
echo "Checking build process ..."
echo
python setup.py build && buildSucceed
