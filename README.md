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

- create `valhalla.yml` in your project (check
  out [examples](https://github.com/logchange/valhalla/tree/master/examples))

```yml
# This file is used by valhalla tool to create release 🌌
# Visit https://github.com/logchange/valhalla and leave a star 🌟
# More info about configuration you can find https://github.com/logchange/valhalla#%EF%B8%8F-configuration ⬅️
extends: # You can extend any file from URL! This helps keep configuration in one place!
  - https://raw.githubusercontent.com/logchange/valhalla/master/valhalla-extends.yml

# Define custom variables which can be used in any string with {}
variables:
  MY_VARIABLE: Some value
git_host: gitlab # your project ci provider, supported [gitlab]  

# define actions which have to happen before release and output should be committed
commit_before_release:
  enabled: True # if this is True commands from before will be performed and committed to branch
  username: Test1234 # git config username
  email: test-valhalla@logchange.dev # git config email
  msg: Releasing version {VERSION} # commit message, you can use string predefined variables
  before: # list of bash commands, you can use string predefined variables, custom variables or system environment variables!
    - echo "test" > some_file4.md
    - mkdir -p changelog/v{VERSION}
    - echo "Super release description for tests generated at {CI_COMMIT_TIMESTAMP}" > changelog/v{VERSION}/version_summary.md

# definition of release which will be created
release:
  name: "Release {VERSION}" # optional filed, you can use string predefined variables (default name is VERSION)
  description:
    # bash command with will be executed and output will be used as 
    # release description, you can use string predefined variables
    from_command: "cat changelog/v{VERSION}/version_summary.md"
  milestones:
    - M {VERSION_MAJOR}.{VERSION_MINOR}
    - Main
  assets: # https://docs.gitlab.com/ee/api/releases/#create-a-release
    links:
      - name: Documentation # you can use string predefined variables
        url: https://google.com/q?={VERSION} # you can use string predefined variables
        link_type: other # The type of the link: other, runbook, image, package.
      - name: Docker Image # you can use string predefined variables
        url: https://dockerhub.com/q?={VERSION} # you can use string predefined variables
        link_type: image # The type of the link: other, runbook, image, package.
        
# definition of tag which will be created
tag:
  name: "Tag {VERSION}" # optional filed, you can use string predefined variables (default name is VERSION) 
  
# define actions which have to happen after release and output should be committed
commit_after_release:
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
  target_branch: hotfix-{VERSION} # optional property (default branch if empty) defining target branch for merge/pull request. Supports regexp
  title: Releasing version {VERSION} and preparation for next development cycle # you can use string predefined variables
  description: Hello world! I have just released {VERSION} # optional filed, you can use string predefined variables
  reviewers:
    - peter.zmilczak # usernames which will be reviews of created MR
    - some_unknown_nick # if username cannot be found you can check logs
```

- Create access token and pass it to CI as environment variable `VALHALLA_TOKEN`
- Update or CI/CD scripts to use valhalla (see below for examples)
- Update your `.gitignore` ! see [link](#-gitignore)

### 🔸 usage

**by branch:**

1. Create branch `release-X.X.X` where `X.X.X` is a name of the version that is going to be released. You can also use
   extensions like `release-2.10.4-RC`. To use different release kind use f.e. `release-hotfix-X.X.X`.
2. Valhalla will do everything for you 🚀

**by `VALHALLA_RELEASE_CMD` env variable:**

1. Set `VALHALLA_RELEASE_CMD` env variable to `release-X.X.X` where `X.X.X` is a name of the version that is going to be
   released. You can also use
   extensions like `release-2.10.4-RC`. To use different release kind use f.e. `release-hotfix-X.X.X`.
2. Valhalla will do everything for you 🚀

### 👨🏻‍👦🏻 inheritance

To simplify managing multimple repositories, you can use `extends:` keyword.

```yml
extends:
  - https://raw.githubusercontent.com/logchange/valhalla/master/valhalla.yml
```

You can point to any URL that is `valhalla.yml` format, and it will be loaded and then override by values from
current file. Currently, you can only inherit once and from one URL, so it means if you inherit from a file, that also
contains
`extends` keyword, it won't be evaluated.

## 🔀 many use cases at once! (different release kinds)

valhalla supports different use cases. F.e. you want to have ability to create minor release and hotfix
but these processes have different steps. You can do it!

What you have to do is to define 2 files:

- valhalla.yml
- valhalla-hotfix.yml

And now, when you want to start one of this process:

- to create minor release using `valhalla.yml` create branch matching regex: `release-*`
- to create hotfix release using `valhalla-hotfix.yml` create branch matching regex: `release-hotfix-*`

This is only example, and you can define any suffix, f.e `valhalla-super-release.yml` needs
branch `release-super-release-*`

*You can only define f.e. `valhalla-minor.yml` and you do not need `valhalla.yml`, but your branches name triggering
release must meet convention*

## 🔢 variables

**Use `{}` to evaluate variable to value f.e. `{FOOBAR}`**

**hierarchy (from most important):**

- predefined variables
- custom variables
- environment variables

So, if there is predefined variable, you cannot override it or if same variable exists in environment,
the value always will be as in predefined. If you define your custom variable and the same exists in environment,
the value will be as defined by you. This hierarchy protects valhalla from errors and gives ability to extends
and override values in custom use cases.

### 🖖 predefined variables

**Use `{}` to evaluate variable to value f.e. `{VERSION}`**

|       name       |                                                                                                                   description                                                                                                                   |
|:----------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|    `VERSION`     |                                                                      value extracted from branch name or `VALHALLA_RELEASE_CMD`, for `release-1.2.14` it will be `1.2.14`                                                                       |
| `VERSION_MAJOR`  |                                                                         value extracted from branch name or `VALHALLA_RELEASE_CMD`, for `release-1.2.14` it will be `1`                                                                         |
| `VERSION_MINOR`  |                                                                         value extracted from branch name or `VALHALLA_RELEASE_CMD`, for `release-1.2.14` it will be `2`                                                                         |
| `VERSION_PATCH`  |                                                                        value extracted from branch name or `VALHALLA_RELEASE_CMD`, for `release-1.2.14` it will be `14`                                                                         |
|  `VERSION_SLUG`  | value extracted from branch name or `VALHALLA_RELEASE_CMD` and with everything except 0-9 and a-z replaced with -. No leading / trailing -, <br/>for `release-1.2.14` it will be `1-2-14`. Use in URLs, host names, domain names and file names |
| `VALHALLA_TOKEN` |                                                                                                token passed to CI runner which execute this job                                                                                                 |

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

### 🐛 environment variables

Valhalla allows you to use any variable defined in your environment system, it is useful f.e when you
are using GitLab CI/CD and you want to
use [GitLab CI/CD predefined variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)
in your `valhalla.yml`.

**Use `{}` to evaluate variable to value f.e. `{HOME}`**

### 🦊 .gitlab-ci.yml

- if using GitLab workflows
  for `merge requests workflow` [(link)](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Workflows/MergeRequest-Pipelines.gitlab-ci.yml)
  you have to add `if: $CI_COMMIT_BRANCH =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/` to global workflow
  configuration

```yml

# Modify your workflow rules to include rule to start pipeline for branch starting with name 
# release- and exclude commits with VALHALLA SKIP (when valhalla commits files we don't want to start pipeline again)
workflows:
  # .... your standard workflows here
  - if: $CI_COMMIT_BRANCH =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/
  - if: $VALHALLA_RELEASE_CMD =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/

# add new stage
stages:
  # .... your standard stages here
  - release

valhalla_release:
  stage: release
  image: logchange/valhalla:1.6.2
  # Prevent from fetching artifacts because it is a problem during committing all files (git add .)
  # https://docs.gitlab.com/ee/ci/jobs/job_artifacts.html#prevent-a-job-from-fetching-artifacts
  dependencies: [ ]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      when: never
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: never
    # we run the job only for branch with name release-
    # and for commits that DOES NOT include VALHALLA SKIP
    # valhalla during committing adds [VALHALLA SKIP] at the end of commit msg
    - if: $CI_COMMIT_BRANCH =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/
    # we run the job when VALHALLA_RELEASE_CMD env variable is present and has name release-
    # and for commits that DOES NOT include VALHALLA SKIP
    # valhalla during committing adds [VALHALLA SKIP] at the end of commit msg
    - if: $VALHALLA_RELEASE_CMD =~ /^release-*/ && $CI_COMMIT_TITLE !~ /.*VALHALLA SKIP.*/
```

### 🚧 .gitignore

Add to your `.gitignore` following rules, please create issue if valhalla commits to many files!
(For GitLab CI/CD add `dependencies: []` which will prevent from committing generated files)

It is important to modify your `.gitignore` when valhalla during `commit_before_release` or
`commit_after_release` phase generates files which you don't want to commit (f.e. maven release plugin or
maven version plugin generates `pom.xml` backup - for mvn version you can also use `-DgenerateBackupPoms=false`)

```
### Valhalla ###
.m2/
```
