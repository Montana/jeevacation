import csv
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class LinkedInContact:
    first_name: str
    last_name: str
    email: Optional[str]
    company: Optional[str]
    position: Optional[str]
    connected_on: Optional[str]
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def search_variations(self) -> List[str]:
        variations = [self.full_name]
        
        variations.append(f"{self.last_name} {self.first_name}")
        
        if ' ' in self.first_name:
            parts = self.first_name.split()
            variations.append(f"{parts[0]} {self.last_name}")
            variations.append(f"{self.first_name} {self.last_name}")
        
        return list(set(variations))


class LinkedInParser:
    
    HEADER_MAPPINGS = {
        'first name': 'first_name',
        'firstname': 'first_name',
        'last name': 'last_name',
        'lastname': 'last_name',
        'email address': 'email',
        'email': 'email',
        'company': 'company',
        'position': 'position',
        'connected on': 'connected_on',
    }
    
    @classmethod
    def parse_csv(cls, csv_path: str) -> List[LinkedInContact]:
        contacts = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                
                header_idx = cls._find_header_row(lines)
                if header_idx is None:
                    raise ValueError("Could not find valid header row in CSV")
                
                reader = csv.DictReader(lines[header_idx:])
                
                normalized_reader = cls._normalize_headers(reader)
                
                for row in normalized_reader:
                    try:
                        contact = cls._parse_row(row)
                        if contact:
                            contacts.append(contact)
                    except Exception as e:
                        logger.warning(f"Error parsing row: {e}")
                        continue
                        
            logger.info(f"Parsed {len(contacts)} contacts from {csv_path}")
            return contacts
            
        except FileNotFoundError:
            logger.error(f"File not found: {csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            raise ValueError(f"Invalid CSV format: {e}")
    
    @classmethod
    def _find_header_row(cls, lines: List[str]) -> Optional[int]:
        for idx, line in enumerate(lines):
            lower_line = line.lower()
            if 'first name' in lower_line or 'firstname' in lower_line:
                return idx
        return None
    
    @classmethod
    def _normalize_headers(cls, reader: csv.DictReader) -> List[Dict[str, str]]:
        normalized_rows = []
        
        for row in reader:
            normalized_row = {}
            for key, value in row.items():
                normalized_key = cls.HEADER_MAPPINGS.get(key.lower().strip(), key.lower().strip())
                normalized_row[normalized_key] = value.strip() if value else None
            normalized_rows.append(normalized_row)
        
        return normalized_rows
    
    @classmethod
    def _parse_row(cls, row: Dict[str, Any]) -> Optional[LinkedInContact]:
        first_name = row.get('first_name')
        last_name = row.get('last_name')
        
        if not first_name or not last_name:
            return None
        
        return LinkedInContact(
            first_name=first_name,
            last_name=last_name,
            email=row.get('email'),
            company=row.get('company'),
            position=row.get('position'),
            connected_on=row.get('connected_on')
        )
    
    @staticmethod
    def filter_common_names(
        contacts: List[LinkedInContact],
        min_name_length: int = 4
    ) -> List[LinkedInContact]:
        COMMON_NAMES = {
            'john smith', 'james johnson', 'michael williams', 'robert brown',
            'mary jones', 'patricia garcia', 'jennifer martinez', 'linda anderson',
            'david taylor', 'michael davis', 'john johnson', 'chris smith'
        }
        
        filtered = []
        for contact in contacts:
            full_name_lower = contact.full_name.lower()
            
            if full_name_lower in COMMON_NAMES:
                logger.info(f"Filtering common name: {contact.full_name}")
                continue
            
            if len(contact.first_name) < min_name_length or len(contact.last_name) < min_name_length:
                logger.info(f"Filtering short name: {contact.full_name}")
                continue
            
            filtered.append(contact)
        
        logger.info(f"Filtered {len(contacts) - len(filtered)} contacts with common names")
        return filtered
