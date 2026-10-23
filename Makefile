.PHONY: all clean build compose-up compose-down compose-restart decrypt

variant ?=local

VALID_VARIANTS := local prod

ifeq ($(filter $(variant),$(VALID_VARIANTS)),)
$(error Invalid variant. Please use one of: $(VALID_VARIANTS))
endif

commit_hash ?= $(shell git rev-parse HEAD)


decrypt:
	@echo "Decrypting environment..."
	@echo "variant: $(variant)"
	@npx shx cp ./envs/.env.$(variant) ./.env
	@dotenvx decrypt -f ./.env -fk ./.env.keys

compose-up:
	@echo "Procura Business DevOps Runner v1.0"
	@echo "----------------------------------"
	@echo "starting docker-compose..."
	@echo "variant: $(variant)"
	@echo "flags: $(flags)"
	@dotenvx run -f ./envs/.env.${variant} -fk ./.env.keys -- docker compose -f ./compose/docker-compose.$(variant).yml -p hrone-$(variant) up $(flags)

compose-down:
	@echo "Procura Business DevOps Runner v1.0"
	@echo "----------------------------------"
	@echo "stopping docker-compose..."
	@echo "variant: $(variant)"
	@docker compose -f ./compose/docker-compose.$(variant).yml -p hrone-$(variant) down


restart:
	@docker compose -f ./compose/docker-compose.$(variant).yml -p hrone-$(variant) --profile core restart

build:
	@echo "building..."
	@yarn build

deploy:
	@echo "deploying..."

clean:
	@echo "cleaning up..."
	@rm -rf dist *.egg-info

test:
	@echo "tests running.."

install:
	@echo "installing..."
	@yarn install