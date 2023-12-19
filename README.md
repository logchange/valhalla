# 🌌 valhalla

🌌 valhalla is a toolkit designed to streamline the release of new versions of software. 🌌

- [dockerhub](https://hub.docker.com/repository/docker/logchange/valhalla/)

### 📐 background and basic concept

- **complex releasing process:** Creating a new software release involves a multitude of intricate steps. This
  complexity
  often results in human errors, time wastage, and a lack of compliance with essential rules and standards.

- **manual workflow:** Traditional release processes rely on manual intervention, making them prone to inefficiencies
  and mistakes, including configuration errors, missed details, and missteps.

- **time inefficiency:** Managing releases manually can be time-consuming. Waiting for human interventions, addressing
  errors, and navigating through intricate procedures can lead to delays.

- **compliance challenges:** Ensuring adherence to specific rules and standards is vital for software releases. However,
  manual processes may overlook or deviate from these guidelines, potentially causing compliance issues or security
  vulnerabilities.

valhalla offers an automated solution to these challenges, streamlining the software release process, minimizing errors,
saving time, and promoting compliance with established regulations.

### ⚙️ configuration

- create `valhalla.yml` in your project (check out [examples](https://github.com/logchange/valhalla/tree/master/examples))
```yml
# This file is used by valhalla tool to create release 🌌
# Visit https://github.com/logchange/valhalla and leave a star 🌟
# More info about configuration you can find https://github.com/logchange/valhalla#%EF%B8%8F-configuration ⬅️
extends: # You can extend any file from URL! This helps keep configuration in one place!
  - https://raw.githubusercontent.com/logchange/valhalla/master/valhalla-extends.yml
git_host: gitlab # your project ci provider, supported [gitlab]  
commit_before_release: # define actions which have to happen before release and output should be committed
  enabled: True # if this is True commands from before will be performed and committed to branch
  username: Test1234 # git config username
  email: test-valhalla@logchange.dev # git config email
  msg: Releasing version {VERSION} # commit message, you can use string predefined variables
  before: # list of bash commands, you can use string predefined variables
    - echo "test" > some_file4.md
    - mkdir -p changelog/v{VERSION}
    - echo "Super release description for tests" > changelog/v{VERSION}/version_summary.md
# definition of release which will be created
release:
  description:
    # bash command with will be executed and output will be used as 
    # release description, you can use string predefined variables
    from_command: "cat changelog/v{VERSION}/version_summary.md"
  assets: # https://docs.gitlab.com/ee/api/releases/#create-a-release
    links:
      - name: Documentation # you can use string predefined variables
        url: https://google.com/q?={VERSION} # you can use string predefined variables
        link_type: other # The type of the link: other, runbook, image, package.
      - name: Docker Image # you can use string predefined variables
        url: https://dockerhub.com/q?={VERSION} # you can use string predefined variables
        link_type: image # The type of the link: other, runbook, image, package.
commit_after_release: # define actions which have to happen after release and output should be committed
  enabled: True
  username: Test1234
  email: test-valhalla@logchange.dev
  msg: Preparation for next development cycle
  before:
    - echo "test" > prepare_next_iteration.md

# define merge request from release breach to your default 
# branch with changes from commit_before_release and commit_after_release
merge_request: 
  enabled: True # if this is True merge request will be created
  title: Releasing version {VERSION} and preparation for next development cycle # you can use string predefined variables
  description: Hello world! I have just released {VERSION} # optional filed, you can use string predefined variables
  reviewers:
    - peter.zmilczak # usernames which will be reviews of created MR
    - some_unknown_nick # if username cannot be found you can check logs
```
- Create access token and pass it to CI as environment variable `VALHALLA_TOKEN`
- Update or CI/CD scripts to use valhalla (see below for examples)

### 🔸 usage

1. Create branch `release-X.X.X` where `X.X.X` is a name of the version that is going to be released. You can also use
   extensions like `release-2.10.4-RC`.
2. Valhalla will do everything for you 🚀

### inheritance

To simplify managing multimple repositories, you can use `extends:` keyword.

```yml
extends:
  - https://raw.githubusercontent.com/logchange/valhalla/master/valhalla.yml
```

You can point to any URL that is `valhalla.yml` format, and it will be loaded and then override by values from
current file. Currently, you can only inherit once and from one URL, so it means if you inherit from a file, that also contains 
`extends` keyword, it won't be evaluated.

**Proxy**

TODO

### 🏭 custom variables

You can define custom variables which can be used by defining them in strings using `{}`

```yml
variables:
  MY_VARIABLE: Some value

merge_request:
  enabled: True
  title: Releasing version {VERSION} and preparation for next development cycle {MY_VARIABLE}
```

**It is really useful with `extends` mechanism, f.e. define general template with `variables`
which will be overriden in child `valhalla.yml`.**

### 🖖 predefined variables

**Use `{}` to evaluate variable to value f.e. `{VERSION}`**

|        name      |                                description                                 |
|:----------------:|:--------------------------------------------------------------------------:|
| `VERSION`        | value extracted from branch name, for `release-1.2.14` it will be `1.2.14` |
| `VALHALLA_TOKEN` | token passed to CI runner which execute this job                           |

### 🦊 .gitlab-ci.yml

- if using GitLab workflows
  for `merge requests workflow` [(link)](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Workflows/MergeRequest-Pipelines.gitlab-ci.yml)
  you have to add `if: $CI_COMMIT_BRANCH =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/` to global workflow configuration

```yml

workflows:
  - if: $CI_COMMIT_BRANCH =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/
  
# add new stage
stages:
  - release
  
valhalla_release:
  stage: release
  image: logchange/valhalla:1.1.0
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: never
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: never
    # we run the job only for branch with name release-
    # and for commits that DOES NOT include VALHALLA SKIP
    # valhalla during committing adds [VALHALLA SKIP] at the end of commit msg
    - if: $CI_COMMIT_BRANCH =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/
```
