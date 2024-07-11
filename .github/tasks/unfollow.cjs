// unfollow everyone not following back
var x = require("if-follow-package");
var id = "prjctimg",
  token = "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";
var f = x(id, token);
f.unfollowAllNotFollowingBack();
