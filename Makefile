DEPLOY_HOST_PROD = agojin
DEV_NAME = agojin


make:


# Django

collectstatic coll::
	@echo "\033[32m" Collect static "\033[0m"
	.m collectstatic --noinput

dev::
	screen -SRR $(DEV_NAME) bin/dev.sh

migrate::
	@echo "\033[32m" Migrate "\033[0m"
	.m migrate

test::
	.m test --noinput tests/


#  git

commit comm:: collectstatic migrate git-commit git-push-origin

git-commit::
	@echo "\033[32m" Git commit "\033[0m"
	gcd; true

git-push-origin::
	@echo "\033[32m" Git push origin"\033[0m"
	bash -c "git push origin master"

git-push-production::
	@echo "\033[32m" Git push production"\033[0m"
	bash -c "git push origin master"

git-push-test::
	@echo "\033[32m" Git push test"\033[0m"
	bash -c "git push test master"


# misc

cd:: commit deploy-prod

cd-prod:: commit deploy-prod

deploy-prod deploy:: git-push-production
	bin/deploy.sh $(DEPLOY_HOST_PROD)
