<p align="center">
  <span style="font-size: 2em">🌌 valhalla 🌌</span>
</p>

<p align="center">
    <a href="https://github.com/logchange/valhalla/graphs/contributors">
        <img src="https://img.shields.io/github/contributors/logchange/valhalla" alt="Contributors"/></a>
    <a href="https://github.com/logchange/valhalla/pulse">
        <img src="https://img.shields.io/github/commit-activity/m/logchange/valhalla" alt="Activity"/></a>
    <a href="https://hub.docker.com/repository/docker/logchange/valhalla/">
        <img src="https://img.shields.io/docker/v/logchange/valhalla?sort=semver&color=green&label=DockerHub" alt="DockerHub"/></a>
    <a href="https://hub.docker.com/repository/docker/logchange/valhalla/">
        <img src="https://img.shields.io/docker/pulls/logchange/valhalla" alt="DockerHub Pulls"/></a>
    <a href="https://codecov.io/gh/logchange/valhalla">
        <img src="https://codecov.io/gh/logchange/valhalla/graph/badge.svg?token=SP3V6ZQ039" alt="codecov"/></a>
</p>

## [Documentation](https://logchange.dev/tools/valhalla/)

Visit **[logchange.dev/tools/valhalla](https://logchange.dev/tools/valhalla/)** to read the full documentation, explore 
usage examples, and learn how to get the most out of Valhalla.


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

- Create `valhalla.yml` in your project (check out [examples](https://github.com/logchange/valhalla/tree/master/examples)) (check out [reference](https://logchange.dev/tools/valhalla/reference/#basic-structure))
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
|     `AUTHOR`     |                                                                                              author of the release (who triggered release process)                                                                                              |


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
