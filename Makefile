make:

deploy: git-push-production
	bin/deploy.sh agojin

django:
	screen -SRR agojin bin/dev

###

cd: comm deploy

coll: collectstatic

collectstatic:
	@echo "\033[32m" Collect static "\033[0m"
	.m collectstatic --noinput

comm: commit

commit: collectstatic migrate git-commit git-push-origin

dev: django

git-commit:
	@echo "\033[32m" Git commit "\033[0m"
	gcd

git-push-origin:
	@echo "\033[32m" Git push origin"\033[0m"
	git push origin;

git-push-production: git-push-origin

migrate:
	@echo "\033[32m" Migrate "\033[0m"
	.m migrate

my: mypy

mypy:
	.mypy
