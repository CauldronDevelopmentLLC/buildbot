# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

from buildbot import interfaces
from buildbot.process.properties import Properties

class BuildRequest:
    """I represent a request to a specific Builder to run a single build.

    I am generated by db.getBuildRequestWithNumber, and am used to tell the
    Build about what it ought to be building. I am also used by the Builder
    to let hook functions decide which requests should be handled first.

    I have a SourceStamp which specifies what sources I will build. This may
    specify a specific revision of the source tree (so source.branch,
    source.revision, and source.patch are used). The .patch attribute is
    either None or a tuple of (patchlevel, diff), consisting of a number to
    use in 'patch -pN', and a unified-format context diff.

    Alternatively, the SourceStamp may specify a set of Changes to be built,
    contained in source.changes. In this case, I may be mergeable with other
    BuildRequests on the same branch.

    @type source: a L{buildbot.sourcestamp.SourceStamp} instance.
    @ivar source: the source code that this BuildRequest use

    @type reason: string
    @ivar reason: the reason this Build is being requested. Schedulers
                  provide this, but for forced builds the user requesting the
                  build will provide a string.

    @type properties: Properties object
    @ivar properties: properties that should be applied to this build
                      'owner' property is used by Build objects to collect
                      the list returned by getInterestedUsers

    @ivar status: the IBuildStatus object which tracks our status

    @ivar submittedAt: a timestamp (seconds since epoch) when this request
                       was submitted to the Builder. This is used by the CVS
                       step to compute a checkout timestamp, as well as the
                       master to prioritize build requests from oldest to
                       newest.
    """

    source = None
    builder = None # XXXREMOVE
    submittedAt = None

    def __init__(self, reason, source, builderName, properties=None):
        assert interfaces.ISourceStamp(source, None)
        self.reason = reason
        self.source = source
        self.builderName = builderName

        self.properties = Properties()
        if properties:
            self.properties.updateFromProperties(properties)

    def canBeMergedWith(self, other):
        return self.source.canBeMergedWith(other.source)

    def mergeWith(self, others):
        return self.source.mergeWith([o.source for o in others])

    def mergeReasons(self, others):
        """Return a reason for the merged build request."""
        reasons = []
        for req in [self] + others:
            if req.reason and req.reason not in reasons:
                reasons.append(req.reason)
        return ", ".join(reasons)

    # IBuildRequestControl

    def cancel(self): # XXXREMOVE
        """Cancel this request. This can only be successful if the Build has
        not yet been started.

        @return: a boolean indicating if the cancel was successful."""
        if self.builder:
            return self.builder.cancelBuildRequest(self)
        return False

    def getSubmitTime(self):
        return self.submittedAt
