# ccctl Community Edition
A command line tool to talk to your Cloud or SaaS service. Community Edition.

## Installation
```bash
$ brew install ccctl
```

## Setup Local LLM
```bash
$ brew install ollama
$ ollama start &
$ ollama pull sqlcoder
```

## Usage
```bash
$ # aws configure / aws sso configure
$ ccctl init aws
$ ccctl aws "How many instances do I have running in eu-central-1?" --llm-endpoint http://localhost:11434 --model sqlcoder
10

# put settings inside ~/.ccctl/config.yaml
# ###
# llm_endpoint: http://localhost:11434
# model: sqlcoder
# ###
$ ccctl init okta
$ ccctl okta "How many groups is Joe Bloggs in?"
3
```

## Main features
- Speak to your SaaS or Cloud (Only AWS and Okta are supported) using natural language queries
- Use an LLM of your choice (supports duckdb-nsql and sqlcoder)
- Fully airgapped solution, no cloud needed

## Contribute
Contributions are welcome! Please follow the steps below to setup your environment.

```bash
$ clone git@github.com:cloudconverse/ccctl.git
$ virtualenv ccctl-venv
$ source ccctl-venv/bin/activate
$ pip install -r requirements.txt
$ git checkout -b "your-contribution"
# do your changes and make a PR and we will review your PR
# if successful we will merge to main branch and your change will appear in the new release.
```