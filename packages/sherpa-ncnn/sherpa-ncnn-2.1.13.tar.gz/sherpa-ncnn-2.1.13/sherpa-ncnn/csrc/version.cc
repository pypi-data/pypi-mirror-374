// sherpa-ncnn/csrc/version.cc
//
// Copyright      2025  Xiaomi Corporation

#include "sherpa-ncnn/csrc/version.h"

namespace sherpa_ncnn {

const char *GetGitDate() {
  static const char *date = "Thu Sep 4 01:13:14 2025";
  return date;
}

const char *GetGitSha1() {
  static const char *sha1 = "a532f235";
  return sha1;
}

const char *GetVersionStr() {
  static const char *version = "2.1.13";
  return version;
}

}  // namespace sherpa_ncnn
