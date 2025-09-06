from __future__ import annotations

from kvcommon.exceptions import DependencyException

try:
    import kubernetes

except ImportError:
    raise DependencyException("KVCommon: Must specify 'k8s' extra to use kubernetes features.")
