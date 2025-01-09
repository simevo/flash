all:
	yarnpkg
	cp node_modules/bootstrap/dist/css/bootstrap.min.css flash/static/css/.
	cp node_modules/bootstrap/dist/css/bootstrap.min.css.map flash/static/css/.
	cp node_modules/bootstrap/dist/js/bootstrap.min.js flash/static/js/.
	cp node_modules/bootstrap/dist/js/bootstrap.min.js.map flash/static/js/.
	cp node_modules/bootstrap-icons/icons/question.svg flash/static/images/.
	cp node_modules/bootstrap-icons/icons/lock.svg flash/static/images/.
