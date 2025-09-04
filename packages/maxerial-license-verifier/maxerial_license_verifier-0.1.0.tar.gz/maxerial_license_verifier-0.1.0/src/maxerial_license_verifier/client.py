import os
import xml.etree.ElementTree as ET
from typing import Optional

import requests


class LicenseVerifier:
    """Verify maXerial license via local activation server and check features.

    Initialize with a path to the license XML file.
    """

    def __init__(self, license_file_path: str, server_endpoint: Optional[str] = None) -> None:
        self.license_file_path = license_file_path
        self.server_endpoint = server_endpoint  # e.g. "/" or "/activate"; default resolved in verify_license
        self.verified: bool = False

    def _get_activation_url(self) -> str:
        port = os.environ.get("ACTIVATION_SERVER_PORT", "61040")
        try:
            int(port)
        except ValueError as exc:
            raise ValueError(
                f"Invalid ACTIVATION_SERVER_PORT '{port}'. It must be an integer string."
            ) from exc
        endpoint = self.server_endpoint or "/"
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"http://127.0.0.1:{port}{endpoint}"

    def verify_license(self, timeout_seconds: float = 5.0) -> bool:
        """Call the activation server with the license file path.

        On HTTP success, sets verified to True. Returns True if request succeeded.
        Attempts to parse a 'license_status' from JSON response if present.
        """
        url = self._get_activation_url()
        try:
            response = requests.post(url, json={"license_path": self.license_file_path}, timeout=timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.verified = False
            raise RuntimeError(f"Failed to contact activation server at {url}: {exc}") from exc

        # If the server returns JSON with 'license_status', we capture it; otherwise we just set verified True.
        license_status: Optional[str] = None
        try:
            data = response.json()
            if isinstance(data, dict) and "license_status" in data:
                license_status = str(data["license_status"]).lower()
        except ValueError:
            # Not JSON; ignore and proceed
            pass

        # Consider success as verification True when the request succeeded.
        self.verified = True
        return license_status == "valid" if license_status is not None else True

    def check_feature(self, feature_name: str) -> bool:
        """Check if the provided feature is present in the license XML.

        Requires self.verified to be True.
        """
        if not self.verified:
            raise RuntimeError("License not verified. Call verify_license() first.")

        try:
            tree = ET.parse(self.license_file_path)
            root = tree.getroot()
        except (OSError, ET.ParseError) as exc:
            raise RuntimeError(f"Failed to read or parse license file '{self.license_file_path}': {exc}") from exc

        # Search for elements or attributes named 'feature'
        # Case-insensitive comparison of feature values
        target = feature_name.strip().lower()

        # 1) Elements named 'feature'
        for feature_el in root.iter():
            if feature_el.tag.lower() == "feature":
                text = (feature_el.text or "").strip().lower()
                if text == target:
                    return True

        # 2) Attributes named 'feature' on any element
        for el in root.iter():
            for attr_name, attr_value in el.attrib.items():
                if attr_name.lower() == "feature" and str(attr_value).strip().lower() == target:
                    return True

        # 3) If features are listed under a collection, e.g., <features><feature>...</feature></features>
        features_parent = None
        for el in root.iter():
            if el.tag.lower() == "features":
                features_parent = el
                break
        if features_parent is not None:
            for child in features_parent:
                if child.tag.lower() == "feature":
                    text = (child.text or "").strip().lower()
                    if text == target:
                        return True

        return False
