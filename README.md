# valhalla

🌌 valhalla is a toolkit designed to streamline the release of new versions of software. 🌌

### background and basic concept

- **complex release process:** Creating a new software release involves a multitude of intricate steps. This complexity
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

### configuration

- if using GitLab workflows
  for `merge requests workflow` [(link)](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Workflows/MergeRequest-Pipelines.gitlab-ci.yml)
  you have to add `if: '$CI_COMMIT_BRANCH =~ /^release-*/` to global workflow configuration

### usage

1. Create branch `release-X.X.X` where `X.X.X` is a name of the version that is going to be released. You can also use
   extensions like `release-2.10.4-RC`.