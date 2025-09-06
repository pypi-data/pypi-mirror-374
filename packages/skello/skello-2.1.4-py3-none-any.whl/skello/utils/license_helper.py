from pathlib import Path
import re
from typing import Optional


class LicenseHelper:
    """Handles license detection, validation, and template mapping."""
    
    # Supported license types and their mappings
    LICENSE_TYPES = {
        'mit': {
            'template': 'LICENSE_MIT.tmpl',
            'classifier': 'MIT License',
            'name': 'MIT License',
            'spdx': 'MIT',
            'patterns': [
                r'mit license',
                r'permission is hereby granted,?\s*free of charge',
                r'the above copyright notice and this permission notice',
                r'without restriction,?\s*including without limitation',
                r'furnished to do so,?\s*subject to the following conditions'
            ]
        },
        'apache': {
            'template': 'LICENSE_APACHE.tmpl', 
            'classifier': 'Apache Software License',
            'name': 'Apache License 2.0',
            'spdx': 'Apache-2.0',
            'patterns': [
                r'apache\s+license',
                r'version\s+2\.0',
                r'licensed under the apache license',
                r'www\.apache\.org/licenses/LICENSE-2\.0',
                r'apache software foundation',
                r'redistribution and use in source and binary forms.*apache'
            ]
        },
        'bsd': {
            'template': 'LICENSE_BSD.tmpl',
            'classifier': 'BSD License',
            'name': 'BSD 3-Clause License',
            'spdx': 'BSD-3-Clause',
            'patterns': [
                r'bsd\s+(3-clause|three-clause|\d-clause)',
                r'redistribution and use in source and binary forms',
                r'neither the name of.*nor the names of',
                r'this software is provided.*as is',
                r'redistributions of source code must retain'
            ]
        },
        'gpl': {
            'template': 'LICENSE_GPL.tmpl',
            'classifier': 'GNU General Public License v3 (GPLv3)',
            'name': 'GNU General Public License v3.0',
            'spdx': 'GPL-3.0-or-later',
            'patterns': [
                r'gnu general public license',
                r'this program is free software',
                r'www\.gnu\.org/licenses',
                r'gpl\s*v?3',
                r'copyleft license',
                r'either version 3 of the license'
            ]
        },
        'lgpl': {
            'template': 'LICENSE_LGPL.tmpl',
            'classifier': 'GNU Lesser General Public License v3 (LGPLv3)',
            'name': 'GNU Lesser General Public License v3.0',
            'spdx': 'LGPL-3.0-or-later',
            'patterns': [
                r'gnu lesser general public license',
                r'lgpl\s*v?3',
                r'library general public license',
                r'either version 3 of the license.*lesser'
            ]
        },
        'mpl': {
            'template': 'LICENSE_MPL.tmpl',
            'classifier': 'Mozilla Public License 2.0 (MPL 2.0)',
            'name': 'Mozilla Public License 2.0',
            'spdx': 'MPL-2.0',
            'patterns': [
                r'mozilla public license',
                r'mpl\s*2\.0',
                r'this source code form is subject to the terms',
                r'mozilla\.org/MPL/2\.0'
            ]
        },
        'unlicense': {
            'template': 'LICENSE_UNLICENSE.tmpl',
            'classifier': 'The Unlicense (Unlicense)',
            'name': 'The Unlicense',
            'spdx': 'Unlicense',
            'patterns': [
                r'this is free and unencumbered software',
                r'released into the public domain',
                r'unlicense\.org',
                r'anyone is free to copy, modify, publish, use'
            ]
        }
    }

    @classmethod
    def get_spdx_license(cls, license_type: str) -> str:
        """Get SPDX license identifier for a license type."""
        license_info = cls.get_license_info(license_type)
        return license_info['spdx']
    
    @classmethod
    def parse_license_spec(cls, license_spec: str = 'mit') -> tuple[str, str]:
        """
        Parses license specification from CLI.
        
        Args:
            license_spec: License spec like 'mit', 'apache', or 'mit:John Doe'
            
        Returns:
            Tuple of (license_type, author_name)
            
        Examples:
            'mit' -> ('mit', None)
            'apache:John Doe' -> ('apache', 'John Doe')
        """
        if ':' in license_spec:
            license_type, author_name = license_spec.split(':', 1)
            return license_type.lower().strip(), author_name.strip()
        
        return license_spec.lower().strip(), None
    
    @classmethod
    def get_license_info(cls, license_type: str) -> dict:
        """
        Gets license information for a given type.
        
        Args:
            license_type: License type identifier
            
        Returns:
            Dict with template, classifier, and name info
        """
        license_type = license_type.lower()
        
        if license_type not in cls.LICENSE_TYPES:
            print(f"⚠️  Unknown license type '{license_type}', defaulting to MIT")
            license_type = 'mit'
        
        return cls.LICENSE_TYPES[license_type]
    
    @classmethod
    def detect_license(cls, target_dir: Path) -> str:
        """
        Detects license type from an existing LICENSE file and returns the LICENSE_TYPE.
        
        Args:
            target_dir: Directory to check for LICENSE file
            
        Returns:
            Detected license type (e.g., 'mit', 'apache', etc.)
        """
        for license_filename in ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'COPYING']:
            license_file = target_dir / license_filename
            if license_file.exists():
                try:
                    license_content = license_file.read_text().lower()
                    
                    # Use pattern-based detection
                    detected_type = cls._analyze_license_content(license_content)
                    if detected_type:
                        return detected_type
                        
                except Exception as e:
                    print(f"Error reading {license_file}: {e}")
        
        return 'mit'  # Default fallback
    
    @classmethod
    def _analyze_license_content(cls, content: str) -> Optional[str]:
        """
        Analyze license file content to determine license type.
        
        Args:
            content: License file content (lowercase)
            
        Returns:
            License type key or None if not detected
        """
        # Score each license type based on pattern matches
        scores = {}
        
        for license_type, info in cls.LICENSE_TYPES.items():
            score = 0
            for pattern in info['patterns']:
                if re.search(pattern, content, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                scores[license_type] = score
        
        # Return the license type with the highest score
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Returns list of supported license types."""
        return list(cls.LICENSE_TYPES.keys())