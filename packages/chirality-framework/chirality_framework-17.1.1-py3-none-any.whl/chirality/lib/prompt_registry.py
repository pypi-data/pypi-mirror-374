"""
Prompt Registry for Chirality Framework

Loads and validates maintainer-authored prompt assets from metadata.yml.
Provides access to versioned prompt assets with integrity checking.
"""

import hashlib
import yaml
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class AssetInfo:
    """Information about a prompt asset."""

    id: str
    path: str
    sha256: str
    version: str
    size_bytes: int
    last_modified: str
    text: str  # Loaded content


class PromptRegistry:
    """
    Registry for maintainer-authored prompt assets.

    Loads metadata.yml and validates each asset against its SHA256 and size.
    Caches asset contents in memory for performance.
    """

    def __init__(self, assets_dir: Optional[Path] = None):
        """
        Initialize registry with assets directory.

        Args:
            assets_dir: Path to prompt_assets directory.
                       Defaults to chirality/prompt_assets/
        """
        if assets_dir is None:
            # Default to chirality/prompt_assets relative to this file
            current_dir = Path(__file__).parent.parent
            assets_dir = current_dir / "prompt_assets"

        self.assets_dir = Path(assets_dir)
        self.metadata_file = self.assets_dir / "metadata.yml"
        self._assets: Dict[str, AssetInfo] = {}
        self._loaded = False

    def load(self) -> None:
        """Load and validate all assets from metadata.yml."""
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")

        # Load metadata
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        registry_version = metadata.get("registry_version", "1.0")
        if registry_version != "1.0":
            raise ValueError(f"Unsupported registry version: {registry_version}")

        # Load each asset
        for asset_data in metadata.get("assets", []):
            asset_id = asset_data["id"]
            asset_path = self.assets_dir / asset_data["path"]

            # Validate file exists
            if not asset_path.exists():
                raise FileNotFoundError(f"Asset file not found: {asset_path}")

            # Load content
            with open(asset_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Validate SHA256
            actual_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
            expected_sha256 = asset_data["sha256"]
            if actual_sha256 != expected_sha256:
                raise ValueError(
                    f"SHA256 mismatch for {asset_id}: "
                    f"expected {expected_sha256}, got {actual_sha256}"
                )

            # Validate size
            actual_size = len(content.encode("utf-8"))
            expected_size = asset_data["size_bytes"]
            if actual_size != expected_size:
                raise ValueError(
                    f"Size mismatch for {asset_id}: "
                    f"expected {expected_size} bytes, got {actual_size} bytes"
                )

            # Store asset info
            self._assets[asset_id] = AssetInfo(
                id=asset_id,
                path=asset_data["path"],
                sha256=expected_sha256,
                version=asset_data["version"],
                size_bytes=expected_size,
                last_modified=asset_data["last_modified"],
                text=content,
            )

        self._loaded = True

    def get(self, asset_id: str) -> AssetInfo:
        """
        Get asset by ID.

        Args:
            asset_id: Asset identifier (e.g., 'system', 'station.evaluation')

        Returns:
            AssetInfo with loaded text content

        Raises:
            KeyError: If asset_id not found
            RuntimeError: If registry not loaded
        """
        if not self._loaded:
            self.load()

        if asset_id not in self._assets:
            available = list(self._assets.keys())
            raise KeyError(f"Asset '{asset_id}' not found. Available: {available}")

        return self._assets[asset_id]

    def get_text(self, asset_id: str) -> str:
        """Get asset text content directly."""
        return self.get(asset_id).text

    def list_assets(self) -> Dict[str, str]:
        """
        List all available assets.

        Returns:
            Dict mapping asset_id -> version
        """
        if not self._loaded:
            self.load()

        return {aid: asset.version for aid, asset in self._assets.items()}

    def get_provenance(self, asset_id: str) -> Dict[str, str]:
        """
        Get provenance information for an asset.

        Returns:
            Dict with id, sha256, version for provenance logging
        """
        asset = self.get(asset_id)
        return {"id": asset.id, "sha256": asset.sha256, "version": asset.version}


# Global registry instance
_registry: Optional[PromptRegistry] = None


def get_registry() -> PromptRegistry:
    """Get the global prompt registry instance."""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry
