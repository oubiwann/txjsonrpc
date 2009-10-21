#BACKUP_SETUP=setup.py.backup
#UPLOAD_SETUP=upload_setup.py
#./admin/generateUploadSetup.py
#mv setup.py $BACKUP_SETUP
#mv $UPLOAD_SETUP setup.py
python setup.py sdist upload --show-response
#rm setup.py
#mv setup.py $UPLOAD_SETUP
#mv $BACKUP_SETUP to setup.py

