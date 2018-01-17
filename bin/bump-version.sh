#!/usr/bin/env bash


# * bump semver of module
# * update changelog

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT=`realpath "${DIR}/.."`

TARGET_BRANCH="master"
CURRENT_BRANCH=`git rev-parse --abbrev-ref HEAD`
if [[ ${CURRENT_BRANCH} != ${TARGET_BRANCH} ]]; then
   echo "we should bump module version only in '${TARGET_BRANCH}' branch"
   exit 1
fi

echo 'lets bump to new version and update changelog file'


PATH_TO_THE_VERSION="${ROOT}/themessage_server/version.txt"

version=`cat ${PATH_TO_THE_VERSION}`
versions=`git tag --list`

echo "grab version file ${PATH_TO_THE_VERSION}"
echo "current version is ${version}"

#increase patch

target_version=$1

version_array=( ${version//./ } )
major_version=${version_array[0]}
minor_version=${version_array[1]}
patch_version=${version_array[2]}

# major, minor, patch
case ${target_version} in
    major)
    new_major_version=$((major_version + 1))
    new_minor_version=0
    new_patch_version=0
    echo "applied major update"
    shift
    ;;
    minor)
    new_major_version=${major_version}
    new_minor_version=$((minor_version + 1))
    new_patch_version=0
    echo "applied minor update"
    shift
    ;;
    *)
    new_major_version=${major_version}
    new_minor_version=${minor_version}
    new_patch_version=$((patch_version + 1))
    target_version=patch
    echo "applied patch"
    ;;
esac

next_version="${new_major_version}.${new_minor_version}.${new_patch_version}"

echo "next version is ${next_version}"

echo ${next_version} > ${PATH_TO_THE_VERSION}
echo "updated version file"


if [[ ${versions} == *${next_version}* ]]; then
   echo 'already has this version'
   exit 1
fi

git commit -am ":rocket: bump to ${next_version}"
git tag ${next_version}
git push
git push --tag


# update CHANGELOG and skip "patch" version
if [[ ${target_version} == "patch" ]]; then
    echo "don't update changelog for a patch";
else
    echo "start change log generation:"

    github_changelog_generator;

    echo "changelog was generated"

    git commit -am ":scroll: changelog to ${next_version}"
    git push
fi

# don't need to deploy yet
# ${DIR}/deploy.sh
