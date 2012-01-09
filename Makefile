PROJ := txjsonrpc
GITHUB_REPO := github.com:oubiwann/$(PROJ).git
GOOGLE_REPO := code.google.com/p/twisted-jsonrpc
LP_REPO := lp:$(PROJ)
MSG_FILE ?= MSG
TMP_FILE ?= /tmp/MSG
VIRT_DIR ?= .txjsonrpc-venv
VERSION := $(shell python txjsonrpc/scripts/getVersion.py)

bzr-2-git:
	git init && bzr fast-export `pwd` | git fast-import && git reset HEAD
	git remote add origin git@github.com:oubiwann/$(PROJ).git
	git push -u origin master

clean:
	find ./ -name "*~" -exec rm {} \;
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;
	find . -name "*.sw[op]" -exec rm {} \;
	rm -rf $(MSG_FILE) $(MSG_FILE).backup _trial_temp/ build/ dist/ MANIFEST \
		CHECK_THIS_BEFORE_UPLOAD.txt *.egg-info

msg:
	-@rm $(MSG_FILE)
	@git diff ChangeLog |egrep -v '^\+\+\+'|egrep '^\+.*'|sed -e 's/^+//' >> $(MSG_FILE)
.PHONY: msg

commit: msg
	bzr commit --show-diff --file=$(MSG_FILE)
	@echo '!!! REMOVE THIS LINE !!!' >> $(TMP_FILE)
	@cat $(MSG_FILE) >> $(TMP_FILE)
	@mv $(TMP_FILE) $(MSG_FILE)
	git commit -a -v -t $(MSG_FILE)
	mv $(MSG_FILE) $(MSG_FILE).backup
	touch $(MSG_FILE)

push:
	git push --all git@$(GITHUB_REPO)
	bzr push $(LP_REPO)
	git push --all https://$(GOOGLE_REPO)

push-tags:
	git push --tags git@$(GITHUB_REPO)
	git push --tags https://$(GOOGLE_REPO)

push-all: push push-tags
.PHONY: push-all

commit-push: commit push-all
.PHONY: commit-push

stat: msg
	@echo
	@echo "### Changes ###"
	@echo
	-@cat $(MSG_FILE)
	@echo
	@echo "### Git working branch status ###"
	@echo
	@git status -s
	@echo
	@echo "### Git branches ###"
	@echo
	@git branch
	@echo 
	@echo "### Bzr status ###"
	@echo
	@bzr stat
	@echo

status: stat
.PHONY: status

todo:
	git grep -n -i -2 XXX
.PHONY: todo

build:
	python setup.py build
	python setup.py sdist

build-docs:
	cd docs/sphinx; make html

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

check-integration:
# placeholder for integration tests
.PHONY: check-integration

version:
	@echo $(VERSION)

virtual-build: SUB_DIR ?= test-build
virtual-build: DIR ?= $(VIRT_DIR)/$(SUB_DIR)
virtual-build: clean build
	mkdir -p $(VIRT_DIR)
	-test -d $(DIR) || virtualenv $(DIR)
	@. $(DIR)/bin/activate
	-test -e $(DIR)/bin/twistd || $(DIR)/bin/pip install twisted
	-test -e $(DIR)/bin/rst2html.py || $(DIR)/bin/pip install docutils
	$(DIR)/bin/pip uninstall -vy txJSON_RPC
	rm -rf $(DIR)/lib/python2.7/site-packages/txJSON*
	$(DIR)/bin/easy_install-2.7 ./dist/txJSON*

clean-virt: clean
	rm -rf $(VIRT_DIR)

virtual-build-clean: clean-virt build virtual-build
.PHONY: virtual-build-clean

register:
	python setup.py register

upload: check
	python setup.py sdist upload --show-response
