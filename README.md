# valhalla

🌌 valhalla is a toolkit designed to streamline the release of new versions of software. 🌌

### configuration

- if using GitLab workflows
  for `merge requests workflow` [(link)](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Workflows/MergeRequest-Pipelines.gitlab-ci.yml)
  you have to add `if: '$CI_COMMIT_BRANCH =~ /^release-*/` to global workflow configuration

### usage

1. Create branch `release-X.X.X` where `X.X.X` is a name of the version that is going to be released. You can also use extensions like `release-2.10.4-RC`.