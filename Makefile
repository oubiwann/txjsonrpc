PROJ := txjsonrpc

bzr-2-git:
	git init && bzr fast-export `pwd` | git fast-import && git reset HEAD
	git remote add origin git@github.com:oubiwann/$(PROJ).git
	git push -u origin master

clean:
	find ./ -name "*~" -exec rm {} \;
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;
	find . -name "*.sw[op]" -exec rm {} \;
	rm -rf MSG.backup _trial_temp/ build/ dist/ MANIFEST \
		CHECK_THIS_BEFORE_UPLOAD.txt *.egg-info


stat:
	@echo "Changes:"
	@cat MSG
	@echo
	@echo "Bazzar working dir status:"
	@echo
	@echo -n "Current revision: "
	@bzr revno
	@bzr stat


todo:
	git grep -n -i -2 XXX


build:
	python setup.py build
	python setup.py sdist


check-docs: files = "README"
check-docs:
	@echo "noop"


check-examples: files = "examples/*.py"
check-examples:
	@echo "noop"

check-dist:
	@echo "Need to fill this in ..."

check: build check-docs check-examples
	trial $(PROJ)

build-docs:
	cd docs/sphinx; make html

commit:
	bzr commit --show-diff
	git commit -a -v

msg-file:
	git diff ChangeLog|egrep '^\+'|egrep -v '^\+{3}'|sed -e 's/^\+//'> MSG

commit-msg: msg-file
	bzr commit --file=MSG
	git commit -a -F MSG


push: commit clean
	bzr push lp:$(PROJ)
	git push origin master


push-msg: commit-msg clean
	bzr push lp:$(PROJ)
	git push origin master
	mv MSG MSG.backup
	touch MSG

register:
	python setup.py register

upload: check
	python setup.py sdist upload --show-response

upload-docs: build-docs
	python setup.py upload_docs --upload-dir=docs/html/
